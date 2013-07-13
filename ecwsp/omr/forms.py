import floppyforms as forms
import ecwsp.gumby_forms as forms
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.forms.formsets import DELETION_FIELD_NAME
from django.contrib.admin.widgets import FilteredSelectMultiple
from django import template
from django.template import Context
from django.forms.widgets import RadioSelect

from ajax_select.fields import AutoCompleteSelectMultipleField, AutoCompleteSelectField

from ecwsp.omr.models import *
from ecwsp.sis.models import Student

class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ('name', 'school_year', 'teachers', 'department', 'marking_period', 'courses')
    teachers = AutoCompleteSelectMultipleField('faculty', required=True, help_text="")
    students = forms.ModelMultipleChoiceField(
        queryset = Student.objects.filter(inactive=False),
        widget = forms.SelectMultiple(attrs={'class':'multiselect'}),
        required = False
        )
    quick_number_questions = forms.IntegerField(max_value=100, min_value=1, required=False)
    quick_number_answers = forms.IntegerField(max_value=6, min_value=2, required=False)
    
    def save(self, *args, **kwargs):
        instance = super(TestForm, self).save(*args, **kwargs)
        instance.enroll_students(self.cleaned_data['students'])
        return instance

class QuestionBenchmarkForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['benchmarks',]
    benchmarks = AutoCompleteSelectMultipleField('benchmark', required=False)
        
