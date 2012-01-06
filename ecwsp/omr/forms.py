from django import forms
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
    teachers = AutoCompleteSelectMultipleField('faculty', required=True)
    students = forms.ModelMultipleChoiceField(queryset=Student.objects.filter(inactive=False), widget=FilteredSelectMultiple("Students",False,attrs={'rows':'10'}), required=False)
    
    def save(self, *args, **kwargs):
        instance = super(TestForm, self).save(*args, **kwargs)
        instance.enroll_students(self.cleaned_data['students'])
        return instance

class TestQuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        widgets = {
            'test': forms.HiddenInput,
        }
    is_true = forms.ChoiceField(widget=forms.Select, choices=((True,"True"),(False,"False")))
    benchmarks = AutoCompleteSelectMultipleField('benchmark', required=False)
    themes = AutoCompleteSelectMultipleField('theme', required=False)
    save_to_bank = forms.BooleanField(required=False, initial=True)
        
class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
    def as_custom(self):
        t = template.loader.get_template('omr/answer_form.html')
        return t.render(Context({'answer': self},))
        
AnswerFormSet = inlineformset_factory(Question, Answer, extra=0, form=AnswerForm)
NewAnswerFormSet = inlineformset_factory(Question, Answer, extra=2, form=AnswerForm)

class EditAnswerInstanceForm(forms.ModelForm):
    class Meta:
        model = AnswerInstance
        fields = ['answer','question','points_earned']
        widgets = {'question':forms.HiddenInput, 'points_earned':forms.HiddenInput,}
        
class ManualEditAnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        widgets = {
            input: radiobutton
        }
        


#https://docs.djangoproject.com/en/dev/ref/forms/widgets/