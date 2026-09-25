from django.shortcuts import render, get_object_or_404
from .models import Course
from payments.models import UserCourseAccess

def course_list(request):
    courses = Course.objects.all()
    user_purchased_course_ids = set()
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            user_purchased_course_ids = set(courses.values_list('id', flat=True))
        else:
            user_purchased_course_ids = {
                access.course_id for access in UserCourseAccess.objects.filter(
                    user=request.user, is_active=True,
                ) if access.is_valid_now()
            }
    return render(request, 'courses/index.html', {
        'courses': courses,
        'user_purchased_course_ids': user_purchased_course_ids,
    })

def course_detail(request, pk):
    course = get_object_or_404(
        Course.objects.prefetch_related('objectives', 'chapters__lessons'),
        pk=pk,
    )
    has_access = False
    course_access = None
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            has_access = True
        else:
            course_access = UserCourseAccess.objects.filter(
                user=request.user, course=course, is_active=True,
            ).first()
            has_access = bool(course_access and course_access.is_valid_now())

    return render(request, 'courses/course.html', {
        'course': course,
        'has_access': has_access,
        'course_access': course_access,
    })

