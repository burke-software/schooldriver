from django import forms
from django.forms.widgets import CheckboxSelectMultiple
from django.contrib.auth.models import User
from django.contrib.localflavor.us.forms import *

from ajax_select.fields import AutoCompleteSelectMultipleField, AutoCompleteSelectField

from ecwsp.admissions.models import *
from ecwsp.sis.models import SchoolYear

class MonthYearField(forms.MultiValueField):
    def compress(self, data_list):
        if data_list:
            return datetime.date(year=int(data_list[1]), month=int(data_list[0]), day=1)
        return datetime.date.today()
        

class ApplicantForm(forms.ModelForm):
    class Meta:
        model = Applicant
    
    ssn = USSocialSecurityNumberField(required=False)
    siblings = AutoCompleteSelectMultipleField('all_student', required=False)
    parent_guardians = AutoCompleteSelectMultipleField('emergency_contact', required=False)
    
        
class ContactLogForm(forms.ModelForm):
    class Meta:
        model = ContactLog
        
class ReportForm(forms.Form):
    school_year = forms.ModelChoiceField(SchoolYear.objects.all())