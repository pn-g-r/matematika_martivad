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


class StudentCommentForm(forms.Form):
    text = forms.CharField(
        label="კომენტარი",
        min_length=1,
        max_length=1000,
        widget=forms.Textarea(attrs={
            "rows": 3,
            "placeholder": "დაწერეთ კომენტარი...",
            "class": "comment-form__input",
        }),
    )

    def clean_text(self):
        text = (self.cleaned_data.get("text") or "").strip()
        if not text:
            raise forms.ValidationError("კომენტარი ცარიელი არ უნდა იყოს.")
        return text
