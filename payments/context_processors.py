from django.utils import timezone
from .models import UserCourseAccess
from courses.models import Course

def paid_user_context(request):
    """
    Provides paid course navigation context for logged-in students.
    Admins and superusers are excluded per business requirements.
    """
    paid_course = None
    paid_courses = []
    if request.user.is_authenticated and not request.user.is_staff and not request.user.is_superuser:
        now = timezone.now()
        active_accesses = (
            UserCourseAccess.objects.filter(
                user=request.user,
                is_active=True,
                expires_at__gt=now,
                course__isnull=False,
            )
            .select_related('course')
            .order_by('-updated_at')
        )
        seen_course_ids = set()
        for access in active_accesses:
            if access.course_id in seen_course_ids:
                continue
            seen_course_ids.add(access.course_id)
            paid_courses.append(access.course)
        if paid_courses:
            paid_course = paid_courses[0]
            paid_courses.sort(key=lambda course: (course.order, course.title))

    return {
        'paid_course': paid_course,
        'paid_courses': paid_courses,
    }

