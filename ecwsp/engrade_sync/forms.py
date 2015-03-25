from django import forms

from ecwsp.schedule.models import MarkingPeriod
from ecwsp.sis.models import Faculty


class SetupCourseForm(forms.Form):
    marking_period = forms.ModelChoiceField(MarkingPeriod.objects.all())


class GradeSyncForm(forms.Form):
    marking_period = forms.ModelChoiceField(MarkingPeriod.objects.all())
    teachers = forms.ModelMultipleChoiceField(
        Faculty.objects.filter(is_active=True, teacher=True))
    include_comments = forms.BooleanField(
        required=False, initial=True)
