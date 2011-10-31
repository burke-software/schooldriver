from django import forms
from django.forms.widgets import CheckboxSelectMultiple, TextInput
from django.contrib.auth.models import User
from django.contrib.localflavor.us.forms import *

from ajax_select.fields import AutoCompleteSelectMultipleField, AutoCompleteSelectField

from ecwsp.admissions.models import *
from ecwsp.sis.models import SchoolYear

class NumberInput(TextInput):
    input_type = 'number'

class MonthYearField(forms.MultiValueField):
    def compress(self, data_list):
        if data_list:
            return datetime.date(year=int(data_list[1]), month=int(data_list[0]), day=1)
        return datetime.date.today()
        

class ApplicantForm(forms.ModelForm):
    class Meta:
        model = Applicant
        widgets = {
            'total_income': NumberInput(attrs={'style':'text-align:right;','step':.01}),
            'adjusted_available_income': NumberInput(attrs={'style':'text-align:right;','step':.01}),
            'calculated_payment': NumberInput(attrs={'style':'text-align:right;','step':.01}),
        }
    
    ssn = USSocialSecurityNumberField(required=False, label="SSN")
    siblings = AutoCompleteSelectMultipleField('all_student', required=False)
    parent_guardians = AutoCompleteSelectMultipleField('emergency_contact', required=False)
    application_decision_by = AutoCompleteSelectField('faculty_user',required=False)
    
        
class ContactLogForm(forms.ModelForm):
    class Meta:
        model = ContactLog
        
class ReportForm(forms.Form):
    school_year = forms.ModelChoiceField(SchoolYear.objects.all())