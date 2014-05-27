from django import forms
from django.forms.widgets import CheckboxSelectMultiple, TextInput
from localflavor.us.forms import *
from localflavor.us.us_states import STATE_CHOICES
from django.core.validators import RegexValidator
import re
import autocomplete_light
from localflavor.us import forms as us_forms

from ecwsp.administration.models import Template
from ecwsp.admissions.models import AdmissionLevel, Applicant
from ecwsp.sis.models import SchoolYear

class NumberInput(TextInput):
    input_type = 'number'

class MonthYearField(forms.MultiValueField):
    def compress(self, data_list):
        if data_list:
            return datetime.date(year=int(data_list[1]), month=int(data_list[0]), day=1)
        return datetime.date.today()
        

class InquiryForm(forms.ModelForm):
    class Meta:
        model = Applicant
        fields = ('fname', 'lname', 'mname', 'sex', 'bday', 'street', 'city', 'state',
                  'zip', 'parent_email', 'family_preferred_language',
                  'siblings', 'year', 'ethnicity', 'hs_grad_yr', 'hs_grad_yr', 'religion',
                  'country_of_birth', 'heard_about_us', 'present_school_typed',
                  'present_school_type_typed')
    ethnicity_other = forms.CharField(required=False)
    language_other = forms.CharField(required=False)
    religion_other = forms.CharField(required=False)
    
    # Parent
    p_lname = forms.CharField(required=False)
    p_fname = forms.CharField(required=False)
    p_relationship_to_child = forms.ChoiceField(required=False, choices=(('Mother','Mother'),('Father','Father'),('Guardian','Guardian')))
    p_address = forms.CharField(required=False)
    p_city = forms.CharField(required=False)
    p_state = us_forms.USStateField(required=False, widget=forms.Select(choices=STATE_CHOICES))
    p_zip = forms.CharField(required=False)
    p_home = us_forms.USPhoneNumberField(required=False)
    p_work = us_forms.USPhoneNumberField(required=False)
    p_work_ext = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:3em;'}))
    p_mobile = us_forms.USPhoneNumberField(required=False)
    p_email = forms.EmailField(required=False)
    
    spam_regex = re.compile(r'^[5\-]+$')
    spam = forms.CharField(required=True, validators=[RegexValidator(regex=spam_regex)])
        


class ApplicantForm(autocomplete_light.ModelForm):
    class Meta:
        model = Applicant
        widgets = {
            'total_income': NumberInput(attrs={'style':'text-align:right;','step':.01}),
            'adjusted_available_income': NumberInput(attrs={'style':'text-align:right;','step':.01}),
            'calculated_payment': NumberInput(attrs={'style':'text-align:right;','step':.01}),
        }
    
    ssn = USSocialSecurityNumberField(required=False, label="SSN")
    
        
class ReportForm(forms.Form):
    school_year = forms.ModelMultipleChoiceField(SchoolYear.objects.all())
    
class TemplateReportForm(forms.Form):
    school_year = forms.ModelMultipleChoiceField(SchoolYear.objects.all())
    level = forms.ModelMultipleChoiceField(AdmissionLevel.objects.all())
    ready_for_export = forms.NullBooleanField()
    template = forms.ModelChoiceField(Template.objects.all())
    
    
    
