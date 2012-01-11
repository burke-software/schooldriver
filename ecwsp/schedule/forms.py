from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.safestring import mark_safe
from django.contrib.localflavor.us.forms import *
from django.conf import settings

from ecwsp.schedule.models import *
from ecwsp.sis.models import *
from ecwsp.sis.forms import *
from ajax_filtered_fields.forms import ManyToManyByRelatedField
from decimal import Decimal
from datetime import datetime, date

class EnrollForm(forms.Form):
    students = ManyToManyByRelatedField(Student, 'year', include_blank=False, required=False)
    cohorts = forms.ModelMultipleChoiceField(queryset=Cohort.objects.all(), required=False)
    class Media:
        js = (
            settings.ADMIN_MEDIA_PREFIX + "js/SelectBox.js",
            settings.ADMIN_MEDIA_PREFIX + "js/SelectFilter2.js",
            '/static/js/jquery.js',
            '/static/js/ajax_filtered_fields.js',
        )

class MarkingPeriodSelectForm(forms.Form):
    marking_period = forms.ModelChoiceField(queryset=MarkingPeriod.objects.filter(active=True))

class EngradeSyncForm(MarkingPeriodSelectForm):
    include_comments = forms.BooleanField(required=False)
    
class GradeUpload(UploadFileForm, MarkingPeriodSelectForm):
    pass
    
class GradeFilterForm(TimeBasedForm):
    marking_period = forms.ModelMultipleChoiceField(required=False, queryset=MarkingPeriod.objects.all())
    final = forms.BooleanField(required=False)
    each_marking_period = forms.BooleanField(required=False,initial=True)
    grade = forms.CharField(max_length=5,
                            widget=forms.TextInput(attrs={'placeholder': 'Enter Grade Here'}),
                            required=False,
                            help_text="P counts as 100%, F counts as 0%",)
    filter_choices = (
        ("lt", "Less Than"),
        ("lte", "Less Than Equals"),
        ("gt", "Greater Than"),
        ("gte", "Greater Than Equals"),
    )
    gpa = forms.DecimalField(max_digits=5, decimal_places=2, required=False)
    gpa_equality =  forms.ChoiceField(choices=filter_choices)
    filter = forms.ChoiceField(choices=filter_choices)
    filter_times = forms.CharField(max_length=2, required=False, initial="*", widget=forms.TextInput(attrs={'style':'width:20px;'}))
    filter_year = forms.ModelMultipleChoiceField(required=False, queryset=GradeLevel.objects.all())
    in_individual_education_program = forms.BooleanField(required=False)
    #disc
    if 'ecwsp.discipline' in settings.INSTALLED_APPS:
        from ecwsp.discipline.models import DisciplineAction
        filter_disc_action = forms.ModelChoiceField(required=False, queryset=DisciplineAction.objects.all())
        filter_disc = forms.ChoiceField(choices=filter_choices, required=False)
        filter_disc_times = forms.CharField(max_length=2, required=False, widget=forms.TextInput(attrs={'style':'width:20px;'}))
    #attn
    filter_attn = forms.ChoiceField(choices=filter_choices, required=False)
    filter_attn_times = forms.CharField(max_length=2, required=False, widget=forms.TextInput(attrs={'style':'width:20px;'}))
    
class CourseSelectionForm(forms.Form):
    course = forms.ModelChoiceField(queryset=Course.objects.filter(marking_period__school_year__active_year=True).distinct(), required=False)