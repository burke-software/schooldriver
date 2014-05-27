import floppyforms as forms
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.forms.formsets import DELETION_FIELD_NAME
from django.contrib.admin.widgets import FilteredSelectMultiple
from django import template
from django.template import Context
from django.forms.widgets import RadioSelect

import autocomplete_light
from ecwsp.omr.models import *
from ecwsp.sis.models import Student, Cohort

class TestForm(autocomplete_light.ModelForm):
    class Meta:
        model = Test
        fields = ('name', 'school_year', 'teachers', 'department', 'marking_period', 'courses')
        widgets = {
            'name': forms.TextInput,
            'school_year': forms.Select,
            'department': forms.Select,
            'marking_period': forms.Select,
            'course': forms.SelectMultiple(attrs={'size': '10', 'style': 'height:100%;'}),
        }
        
    #teachers = AutoCompleteSelectMultipleField('faculty', required=True, help_text="")
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
        widget = forms.SelectMultiple(attrs={'size': '10', 'style': 'height:100%;'})
    )
    
    def save(self, *args, **kwargs):
        instance = super(TestForm, self).save(*args, **kwargs)
        instance.enroll_students(self.cleaned_data['students'])
        return instance

class QuestionBenchmarkForm(autocomplete_light.ModelForm):
    class Meta:
        model = Question
        fields = ['benchmarks',]
        
class CohortForm(forms.Form):
    cohorts = forms.ModelMultipleChoiceField(
        queryset=Cohort.objects.all(),
        required=False,
        widget=forms.widgets.SelectMultiple(attrs={'size':'12'}),)
