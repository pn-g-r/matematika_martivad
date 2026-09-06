from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from django.db.models import Exists, F, Max, OuterRef, Prefetch, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from urllib.parse import urlencode

from courses.models import Course
from payments.models import PlanType, UserCourseAccess

from .forms import GrantCourseAccessForm

User = get_user_model()
STUDENTS_PER_PAGE = 20
ENROLLMENT_FILTERS = ('all', 'enrolled', 'not_enrolled')
SEARCH_FIELDS = {
    'student_name': 'მოსწავლის სახელი',
    'parent_name': 'მშობლის სახელი',
    'phone': 'ტელეფონის ნომერი',
}


def staff_required(view_func):
    return user_passes_test(lambda u: u.is_active and u.is_staff)(view_func)


def _valid_access_subquery(now):
    return UserCourseAccess.objects.filter(
        user_id=OuterRef('pk'),
        is_active=True,
        expires_at__gt=now,
    )


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


def _student_queryset(status='all', course_id=None, search_field='', search_q=''):
    now = timezone.now()
    active_access_qs = (
        UserCourseAccess.objects.filter(is_active=True)
        .select_related('course')
        .order_by('-expires_at')
    )
    qs = (
        User.objects.filter(is_staff=False, is_superuser=False)
        .annotate(
            latest_enrollment=Max('course_accesses__created_at'),
            has_valid_enrollment=Exists(_valid_access_subquery(now)),
        )
        .order_by(F('latest_enrollment').desc(nulls_last=True), '-date_joined')
        .prefetch_related(Prefetch('course_accesses', queryset=active_access_qs, to_attr='active_accesses'))
    )

    has_search = search_field in SEARCH_FIELDS and bool((search_q or '').strip())
    if not has_search:
        if status == 'enrolled':
            qs = qs.filter(has_valid_enrollment=True)
        elif status == 'not_enrolled':
            qs = qs.filter(has_valid_enrollment=False)

        if course_id:
            qs = qs.filter(
                course_accesses__course_id=course_id,
                course_accesses__is_active=True,
                course_accesses__expires_at__gt=now,
            ).distinct()

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

    return status, course_id, search_field, search_q


def _list_query_params(status='all', course_id=None, search_field='', search_q='', page=None):
    params = {}
    if status and status != 'all':
        params['status'] = status
    if course_id:
        params['course'] = course_id
    if search_field and search_q:
        params['search_field'] = search_field
        params['search_q'] = search_q
    if page:
        params['page'] = page
    return params


def _students_list_url(page=None, status='all', course_id=None, search_field='', search_q=''):
    params = _list_query_params(status, course_id, search_field, search_q, page)
    url = reverse('dashboard:students')
    if params:
        url = f"{url}?{urlencode(params)}"
    return url


@staff_required
def student_list_view(request):
    status, course_id, search_field, search_q = _parse_list_params(request.GET)
    queryset = _student_queryset(
        status=status,
        course_id=course_id,
        search_field=search_field,
        search_q=search_q,
    )
    paginator = Paginator(queryset, STUDENTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))
    list_query = urlencode(_list_query_params(status, course_id, search_field, search_q))
    search_active = bool(search_field and search_q)

    if search_active:
        url_filter_all = _students_list_url(status='all', course_id=course_id)
        url_filter_enrolled = _students_list_url(status='enrolled', course_id=course_id)
        url_filter_not_enrolled = _students_list_url(status='not_enrolled', course_id=course_id)
    else:
        url_filter_all = _students_list_url(status='all', course_id=course_id, search_field=search_field, search_q=search_q)
        url_filter_enrolled = _students_list_url(status='enrolled', course_id=course_id, search_field=search_field, search_q=search_q)
        url_filter_not_enrolled = _students_list_url(status='not_enrolled', course_id=course_id, search_field=search_field, search_q=search_q)

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
            'search_field': search_field,
            'search_q': search_q,
            'search_active': search_active,
            'search_fields': SEARCH_FIELDS,
            'search_field_label': SEARCH_FIELDS.get(search_field, 'ძებნის ველი'),
            'list_query': list_query,
            'url_filter_all': url_filter_all,
            'url_filter_enrolled': url_filter_enrolled,
            'url_filter_not_enrolled': url_filter_not_enrolled,
            'url_clear_search': _students_list_url(status=status, course_id=course_id),
            'courses': Course.objects.order_by('order', 'title'),
        },
    )


@staff_required
@require_POST
def grant_access_view(request, user_id):
    student = get_object_or_404(User, pk=user_id, is_staff=False, is_superuser=False)
    form = GrantCourseAccessForm(request.POST)
    list_status = request.POST.get('list_status', 'all')
    list_course = request.POST.get('list_course', '').strip()
    list_course_id = int(list_course) if list_course.isdigit() else None
    list_search_field = request.POST.get('list_search_field', '').strip()
    list_search_q = request.POST.get('list_search_q', '').strip()
    if list_search_field not in SEARCH_FIELDS:
        list_search_field = ''
        list_search_q = ''
    page = request.POST.get('page')

    redirect_kwargs = dict(
        page=page,
        status=list_status,
        course_id=list_course_id,
        search_field=list_search_field,
        search_q=list_search_q,
    )

    if not form.is_valid():
        messages.error(request, "წვდომის მინიჭება ვერ მოხერხდა. შეამოწმეთ არჩეული კურსი.")
        return redirect(_students_list_url(**redirect_kwargs))

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
    return redirect(_students_list_url(**redirect_kwargs))
