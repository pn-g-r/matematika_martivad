from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Course
from payments.models import UserCourseAccess

def course_list(request):
    courses = Course.objects.all()
    return render(request, 'courses/index.html', {'courses': courses})

def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    has_access = False
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            has_access = True
        else:
            now = timezone.now()
            has_access = UserCourseAccess.objects.filter(
                user=request.user,
                course=course,
                is_active=True,
                expires_at__gt=now
            ).exists()

    return render(request, 'courses/course.html', {
        'course': course,
        'has_access': has_access,
    })

