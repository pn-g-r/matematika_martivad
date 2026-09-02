from django.utils import timezone
from .models import UserCourseAccess
from courses.models import Course

def paid_user_context(request):
    """
    Provides 'paid_course' to templates for logged-in paid students.
    Admins and superusers are excluded per business requirements.
    """
    paid_course = None
    if request.user.is_authenticated and not request.user.is_staff and not request.user.is_superuser:
        now = timezone.now()
        active_access = UserCourseAccess.objects.filter(
            user=request.user,
            is_active=True,
            expires_at__gt=now
        ).select_related('course').order_by('-updated_at').first()
        if active_access:
            paid_course = active_access.course

    return {
        'paid_course': paid_course,
    }

