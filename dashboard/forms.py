from django import forms

from courses.models import Course
from payments.models import PlanType


class GrantCourseAccessForm(forms.Form):
    course = forms.ModelChoiceField(
        label="კურსი",
        queryset=Course.objects.order_by('order', 'title'),
        empty_label="— აირჩიეთ კურსი —",
    )
    plan_type = forms.ChoiceField(
        label="პაკეტი",
        choices=PlanType.choices,
        initial=PlanType.YEARLY,
    )
