from django import forms
from volunteer_track.models import *
from ajax_select.fields import AutoCompleteSelectField
from django.forms import HiddenInput



class inputTimeForm(forms.ModelForm):
    class Meta:
        model = Hours
        widgets = {'student':HiddenInput}
        exclude = ['student']

class newSiteForm(forms.ModelForm):
    class Meta:
        model = Site
        
class siteForm(forms.ModelForm):
    class Meta:
        model = Site
        include = ['site_name']
    query = AutoCompleteSelectField('site', required=True)

class jobDescriptionForm(forms.ModelForm):
    class Meta:
        model = Volunteer
        fields= ['job_description', 'student']
        widgets = {'student':HiddenInput}
        job_description = forms.CharField(widget=forms.Textarea, required=True)