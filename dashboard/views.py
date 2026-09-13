from datetime import datetime, timedelta
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from django.db.models import Exists, F, Max, OuterRef, Prefetch, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from courses.models import Course
from payments.models import OrderStatus, PaymentOrder, PlanType, UserCourseAccess

from .forms import GrantCourseAccessForm, StudentCommentForm
from .models import StudentComment

User = get_user_model()
STUDENTS_PER_PAGE = 20
ENROLLMENT_FILTERS = (
    'all',
    'enrolled',
    'warm_leads',
    'free_access',
    'canceled_renewal',
    'declined_payments',
)
SEARCH_FIELDS = {
    'student_name': 'მოსწავლის სახელი',
    'parent_name': 'მშობლის სახელი',
    'phone': 'ტელეფონის ნომერი',
}


def staff_required(view_func):
    return user_passes_test(lambda u: u.is_active and u.is_staff)(view_func)


def _valid_access_subquery(now, course_id=None):
    filters = {
        'user_id': OuterRef('pk'),
        'is_active': True,
        'expires_at__gt': now,
    }
    if course_id:
        filters['course_id'] = course_id
    return UserCourseAccess.objects.filter(**filters)


def _free_access_subquery(now, course_id=None):
    filters = {
        'user_id': OuterRef('pk'),
        'is_active': True,
        'expires_at__gt': now,
        'last_order__isnull': True,
    }
    if course_id:
        filters['course_id'] = course_id
    return UserCourseAccess.objects.filter(**filters)


def _any_access_subquery(course_id=None):
    filters = {'user_id': OuterRef('pk')}
    if course_id:
        filters['course_id'] = course_id
    return UserCourseAccess.objects.filter(**filters)


def _approved_payment_subquery(course_id=None):
    filters = {
        'user_id': OuterRef('pk'),
        'status': OrderStatus.APPROVED,
    }
    if course_id:
        filters['course_id'] = course_id
    return PaymentOrder.objects.filter(**filters)


def _expiring_on_date_subquery(target_date, course_id=None):
    filters = {
        'user_id': OuterRef('pk'),
        'is_active': True,
        'expires_at__date': target_date,
    }
    if course_id:
        filters['course_id'] = course_id
    return UserCourseAccess.objects.filter(**filters)


def _canceled_renewal_subquery(now, course_id=None):
    filters = {
        'user_id': OuterRef('pk'),
        'is_active': True,
        'expires_at__gt': now,
        'auto_renew': False,
    }
    if course_id:
        filters['course_id'] = course_id
    return UserCourseAccess.objects.filter(**filters)


def _declined_payments_subquery(now, hours=48, course_id=None):
    filters = {
        'user_id': OuterRef('pk'),
        'status': OrderStatus.DECLINED,
        'created_at__gte': now - timedelta(hours=hours),
    }
    if course_id:
        filters['course_id'] = course_id
    return PaymentOrder.objects.filter(**filters)


def _apply_search(qs, search_field, search_q):
    query = (search_q or '').strip()
    if not query or search_field not in SEARCH_FIELDS:
        return qs
    if search_field == 'student_name':
        return qs.filter(student_name__icontains=query)
    if search_field == 'parent_name':
        return qs.filter(parent_name__icontains=query)
    if search_field == 'phone':
        return qs.filter(Q(phone_number__icontains=query) | Q(username__icontains=query))
    return qs


def _student_queryset(status='all', course_id=None, search_field='', search_q='', expiring_date=None):
    now = timezone.now()
    active_access_qs = (
        UserCourseAccess.objects.filter(is_active=True)
        .select_related('course')
        .order_by('-expires_at')
    )
    comments_qs = StudentComment.objects.select_related("author").order_by("-created_at")
    qs = (
        User.objects.filter(is_staff=False, is_superuser=False)
        .annotate(
            latest_enrollment=Max('course_accesses__created_at'),
            has_valid_enrollment=Exists(_valid_access_subquery(now, course_id=course_id)),
        )
        .order_by(F('latest_enrollment').desc(nulls_last=True), '-date_joined')
        .prefetch_related(
            Prefetch('course_accesses', queryset=active_access_qs, to_attr='active_accesses'),
            Prefetch('staff_comments', queryset=comments_qs, to_attr='staff_comment_list'),
        )
    )

    has_search = search_field in SEARCH_FIELDS and bool((search_q or '').strip())
    if not has_search:
        if status == 'enrolled':
            qs = qs.filter(has_valid_enrollment=True)
        elif status == 'warm_leads':
            qs = qs.filter(
                ~Exists(_any_access_subquery(course_id=course_id))
                & ~Exists(_approved_payment_subquery(course_id=course_id))
            )
        elif status == 'free_access':
            qs = qs.filter(Exists(_free_access_subquery(now, course_id=course_id)))
        elif status == 'canceled_renewal':
            qs = qs.filter(Exists(_canceled_renewal_subquery(now, course_id=course_id)))
        elif status == 'declined_payments':
            qs = qs.filter(Exists(_declined_payments_subquery(now, hours=48, course_id=course_id)))
        elif course_id:
            qs = qs.filter(
                course_accesses__course_id=course_id,
                course_accesses__is_active=True,
                course_accesses__expires_at__gt=now,
            ).distinct()

    if expiring_date:
        qs = qs.filter(Exists(_expiring_on_date_subquery(expiring_date, course_id=course_id)))

    qs = _apply_search(qs, search_field, search_q)
    return qs


def _parse_list_params(get_params):
    status = get_params.get('status', 'all')
    if status not in ENROLLMENT_FILTERS:
        status = 'all'

    course_id = get_params.get('course', '').strip()
    if course_id and course_id.isdigit():
        course_id = int(course_id)
        if not Course.objects.filter(pk=course_id).exists():
            course_id = None
    else:
        course_id = None

    search_field = get_params.get('search_field', '').strip()
    if search_field not in SEARCH_FIELDS:
        search_field = ''

    search_q = get_params.get('search_q', '').strip()
    if not search_field:
        search_q = ''

    expiring_date_str = get_params.get('expiring_date', '').strip()
    expiring_date = None
    if expiring_date_str:
        try:
            expiring_date = datetime.strptime(expiring_date_str, '%Y-%m-%d').date()
        except ValueError:
            expiring_date_str = ''
            expiring_date = None

    return status, course_id, search_field, search_q, expiring_date, expiring_date_str


def _list_query_params(status='all', course_id=None, search_field='', search_q='', expiring_date='', page=None):
    params = {}
    if status and status != 'all':
        params['status'] = status
    if course_id:
        params['course'] = course_id
    if search_field and search_q:
        params['search_field'] = search_field
        params['search_q'] = search_q
    if expiring_date:
        params['expiring_date'] = expiring_date
    if page:
        params['page'] = page
    return params


def _students_list_url(page=None, status='all', course_id=None, search_field='', search_q='', expiring_date=''):
    params = _list_query_params(status, course_id, search_field, search_q, expiring_date, page)
    url = reverse('dashboard:students')
    if params:
        url = f"{url}?{urlencode(params)}"
    return url


def _list_redirect_from_post(request):
    list_status = request.POST.get('list_status', 'all')
    list_course = request.POST.get('list_course', '').strip()
    list_course_id = int(list_course) if list_course.isdigit() else None
    list_search_field = request.POST.get('list_search_field', '').strip()
    list_search_q = request.POST.get('list_search_q', '').strip()
    list_expiring_date = request.POST.get('list_expiring_date', '').strip()
    if list_search_field not in SEARCH_FIELDS:
        list_search_field = ''
        list_search_q = ''
    return _students_list_url(
        page=request.POST.get('page'),
        status=list_status,
        course_id=list_course_id,
        search_field=list_search_field,
        search_q=list_search_q,
        expiring_date=list_expiring_date,
    )


@staff_required
def student_list_view(request):
    status, course_id, search_field, search_q, expiring_date, expiring_date_str = _parse_list_params(request.GET)
    queryset = _student_queryset(
        status=status,
        course_id=course_id,
        search_field=search_field,
        search_q=search_q,
        expiring_date=expiring_date,
    )
    paginator = Paginator(queryset, STUDENTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))
    list_query = urlencode(_list_query_params(status, course_id, search_field, search_q, expiring_date_str))
    search_active = bool(search_field and search_q)

    search_args = {'search_field': '', 'search_q': ''} if search_active else {'search_field': search_field, 'search_q': search_q}
    filter_urls = {
        'all': _students_list_url(status='all', course_id=course_id, expiring_date=expiring_date_str, **search_args),
        'enrolled': _students_list_url(status='enrolled', course_id=course_id, expiring_date=expiring_date_str, **search_args),
        'warm_leads': _students_list_url(status='warm_leads', course_id=course_id, expiring_date=expiring_date_str, **search_args),
        'free_access': _students_list_url(status='free_access', course_id=course_id, expiring_date=expiring_date_str, **search_args),
        'canceled_renewal': _students_list_url(status='canceled_renewal', course_id=course_id, expiring_date=expiring_date_str, **search_args),
        'declined_payments': _students_list_url(status='declined_payments', course_id=course_id, expiring_date=expiring_date_str, **search_args),
    }

    filter_tabs = [
        {'id': 'all', 'label': 'ყველა', 'url': filter_urls['all']},
        {'id': 'enrolled', 'label': 'ჩარიცხული', 'url': filter_urls['enrolled']},
        {'id': 'warm_leads', 'label': '🔥 რეგ&გადაუხდელი', 'url': filter_urls['warm_leads']},
        {'id': 'free_access', 'label': '🎁 უფასო წვდომა', 'url': filter_urls['free_access']},
        {'id': 'canceled_renewal', 'label': '⚠️ გაუქმებული გამოწერა', 'url': filter_urls['canceled_renewal']},
        {'id': 'declined_payments', 'label': '❌ უარყოფილი (48 სთ)', 'url': filter_urls['declined_payments']},
    ]

    date_stats = None
    if expiring_date:
        date_accesses = UserCourseAccess.objects.filter(is_active=True, expires_at__date=expiring_date)
        if course_id:
            date_accesses = date_accesses.filter(course_id=course_id)
        will_charge_count = date_accesses.filter(auto_renew=True, plan_type=PlanType.MONTHLY).count()
        will_not_charge_count = date_accesses.filter(Q(auto_renew=False) | Q(plan_type=PlanType.YEARLY)).count()
        date_stats = {
            'total_expiring': will_charge_count + will_not_charge_count,
            'will_charge_count': will_charge_count,
            'will_charge_amount': will_charge_count * 50,
            'will_not_charge_count': will_not_charge_count,
        }

    url_clear_date = _students_list_url(
        status=status,
        course_id=course_id,
        search_field=search_field,
        search_q=search_q,
        expiring_date='',
    )

    return render(
        request,
        'dashboard/students.html',
        {
            'page_obj': page_obj,
            'students': page_obj.object_list,
            'grant_form': GrantCourseAccessForm(),
            'total_students': paginator.count,
            'filter_status': status,
            'filter_course': course_id or '',
            'expiring_date_str': expiring_date_str,
            'date_stats': date_stats,
            'url_clear_date': url_clear_date,
            'search_field': search_field,
            'search_q': search_q,
            'search_active': search_active,
            'search_fields': SEARCH_FIELDS,
            'search_field_label': SEARCH_FIELDS.get(search_field, 'ძებნის ველი'),
            'list_query': list_query,
            'filter_tabs': filter_tabs,
            'url_filter_all': filter_urls['all'],
            'url_filter_enrolled': filter_urls['enrolled'],
            'url_filter_warm_leads': filter_urls['warm_leads'],
            'url_filter_free_access': filter_urls['free_access'],
            'url_filter_canceled_renewal': filter_urls['canceled_renewal'],
            'url_filter_declined_payments': filter_urls['declined_payments'],
            'url_clear_search': _students_list_url(status=status, course_id=course_id, expiring_date=expiring_date_str),
            'courses': Course.objects.order_by('order', 'title'),
        },
    )


@staff_required
@require_POST
def grant_access_view(request, user_id):
    student = get_object_or_404(User, pk=user_id, is_staff=False, is_superuser=False)
    form = GrantCourseAccessForm(request.POST)
    list_url = _list_redirect_from_post(request)

    if not form.is_valid():
        messages.error(request, "წვდომის მინიჭება ვერ მოხერხდა. შეამოწმეთ არჩეული კურსი.")
        return redirect(list_url)

    course = form.cleaned_data['course']
    plan_type = form.cleaned_data['plan_type']
    access = UserCourseAccess.grant_or_renew_access(
        user=student,
        course=course,
        plan_type=plan_type,
        payment_order=None,
        subscription_order_id="",
        rectoken="",
    )
    access.auto_renew = False
    access.last_order = None
    access.subscription_order_id = ""
    access.save(update_fields=['auto_renew', 'last_order', 'subscription_order_id', 'updated_at'])

    messages.success(
        request,
        (
            f"{student.student_name or student.username}-ს მიენიჭა წვდომა "
            f"კურსზე {course.title} ({access.get_plan_type_display()}, "
            f"{access.expires_at:%Y-%m-%d}-მდე)."
        ),
    )
    return redirect(list_url)


@staff_required
@require_POST
def add_student_comment_view(request, user_id):
    student = get_object_or_404(User, pk=user_id, is_staff=False, is_superuser=False)
    form = StudentCommentForm(request.POST)
    list_url = _list_redirect_from_post(request)
    if not form.is_valid():
        messages.error(request, "კომენტარის დამატება ვერ მოხერხდა.")
        return redirect(list_url)

    StudentComment.objects.create(
        student=student,
        author=request.user,
        text=form.cleaned_data["text"],
    )
    messages.success(request, "კომენტარი დამატებულია.")
    return redirect(list_url)


@staff_required
@require_POST
def delete_student_comment_view(request, user_id, comment_id):
    student = get_object_or_404(User, pk=user_id, is_staff=False, is_superuser=False)
    comment = get_object_or_404(StudentComment, pk=comment_id, student=student)
    comment.delete()
    messages.success(request, "კომენტარი წაიშალა.")
    return redirect(_list_redirect_from_post(request))
