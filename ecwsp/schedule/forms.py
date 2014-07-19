import floppyforms as forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.safestring import mark_safe
from localflavor.us.forms import *
from django.conf import settings

from ecwsp.schedule.models import *
from ecwsp.sis.models import *
from ecwsp.sis.forms import *
from decimal import Decimal
from datetime import datetime, date

class EnrollForm(forms.Form):
    students = forms.ModelMultipleChoiceField(
        queryset=Student.objects.all(),
        widget = forms.SelectMultiple(attrs={'class':'multiselect',}),
        required=False)
    cohorts = forms.ModelMultipleChoiceField(
        queryset=Cohort.objects.all(),
        widget = forms.SelectMultiple(attrs={'class': 'field picker', 'style': 'min-height: 400px;'}),
        required=False)

class MarkingPeriodSelectForm(forms.Form):
    marking_period = forms.ModelChoiceField(queryset=MarkingPeriod.objects.filter(active=True))

class EngradeSyncForm(MarkingPeriodSelectForm):
    include_comments = forms.BooleanField(required=False)


class StarOrIntField(forms.CharField):
    def validate(self, value):
        super(StarOrIntField, self).validate(value)
        if not value == "*":
            try:
                int(value)
            except:
                raise ValidationError("Field must be * or an integer.")

class GradeFilterForm(TimeBasedForm):
    marking_period = forms.ModelMultipleChoiceField(required=False, queryset=MarkingPeriod.objects.all())

    filter_choices = (
        ("lt", "Less Than"),
        ("lte", "Less Than Equals"),
        ("gt", "Greater Than"),
        ("gte", "Greater Than Equals"),
    )

    grade = forms.CharField(max_length=5,
                            widget=forms.TextInput(attrs={'placeholder': 'Enter Grade Here'}),
                            required=False,
                            help_text="P counts as 100%, F counts as 0%",)
    grade_filter = forms.ChoiceField(choices=filter_choices)
    grade_times = StarOrIntField(max_length=2, required=False, initial="*", widget=forms.TextInput(attrs={'style':'width:20px;'}))
    final_grade = forms.CharField(max_length=5,
                            widget=forms.TextInput(attrs={'placeholder': 'Enter Grade Here'}),
                            required=False,
                            help_text="P counts as 100%, F counts as 0%",)
    final_grade_filter = forms.ChoiceField(choices=filter_choices)
    final_grade_times = StarOrIntField(max_length=2, required=False, initial="*", widget=forms.TextInput(attrs={'style':'width:20px;'}))

    gpa = forms.DecimalField(max_digits=5, decimal_places=2, required=False)
    gpa_equality =  forms.ChoiceField(choices=filter_choices)
    filter_year = forms.ModelMultipleChoiceField(required=False, queryset=GradeLevel.objects.all())
    in_individual_education_program = forms.BooleanField(required=False)
    #disc
    if 'ecwsp.discipline' in settings.INSTALLED_APPS:
        from ecwsp.discipline.models import DisciplineAction
        filter_disc_action = forms.ModelChoiceField(required=False, queryset=DisciplineAction.objects.all())
        filter_disc = forms.ChoiceField(choices=filter_choices, required=False)
        filter_disc_times = forms.CharField(max_length=2, required=False, widget=forms.TextInput(attrs={'style':'width:20px;'}))
        # Aggregated
        aggregate_disc = forms.ChoiceField(choices=filter_choices, required=False)
        aggregate_disc_times = forms.CharField(max_length=2, required=False, widget=forms.TextInput(attrs={'style':'width:20px;'}))
        aggregate_disc_major = forms.BooleanField(required=False)
    # Absences
    filter_attn = forms.ChoiceField(choices=filter_choices, required=False)
    filter_attn_times = forms.CharField(max_length=2, required=False, widget=forms.TextInput(attrs={'style':'width:20px;'}))
    # Tardies
    filter_tardy = forms.ChoiceField(choices=filter_choices, required=False)
    filter_tardy_times = forms.CharField(max_length=2, required=False, widget=forms.TextInput(attrs={'style':'width:20px;'}))
    
