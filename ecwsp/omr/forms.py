import floppyforms as forms
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.forms.formsets import DELETION_FIELD_NAME
from django.contrib.admin.widgets import FilteredSelectMultiple
from django import template
from django.template import Context
from django.forms.widgets import RadioSelect

from ajax_select.fields import AutoCompleteSelectMultipleField, AutoCompleteSelectField

from ecwsp.omr.models import *
from ecwsp.sis.models import Student, Cohort

class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ('name', 'school_year', 'teachers', 'department', 'marking_period', 'courses')
        widgets = {
            'name': forms.TextInput,
            'school_year': forms.Select,
            'department': forms.Select,
            'marking_period': forms.Select,
            'course': forms.SelectMultiple,

        }
    teachers = AutoCompleteSelectMultipleField('faculty', required=True, help_text="")
    students = forms.ModelMultipleChoiceField(
        queryset = Student.objects.filter(is_active=True),
        widget = forms.SelectMultiple(attrs={'class':'multiselect'}),
        required = False
        )
    quick_number_questions = forms.IntegerField(max_value=100, min_value=1, required=False,
                                               label="Number of Questions")
    quick_number_answers = forms.IntegerField(max_value=6, min_value=2, required=False,
                                             label="Number of Answers",
                                             help_text="Per Question")
    enroll_cohorts = forms.ModelMultipleChoiceField(
        queryset = Cohort.objects.all(),
        required = False,
    )
    
    def save(self, *args, **kwargs):
        instance = super(TestForm, self).save(*args, **kwargs)
        instance.enroll_students(self.cleaned_data['students'])
        return instance

class QuestionBenchmarkForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['benchmarks',]
    benchmarks = AutoCompleteSelectMultipleField('benchmark', required=False)
        
class CohortForm(forms.Form):
    cohorts = forms.ModelMultipleChoiceField(
        queryset=Cohort.objects.all(),
        required=False,
        widget=forms.widgets.SelectMultiple(attrs={'size':'12'}),)
