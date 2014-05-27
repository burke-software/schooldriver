from django import forms
from .models import Hours, Site, VolunteerSite, SiteSupervisor
from django.forms import HiddenInput, ChoiceField
from django.contrib.admin import widgets as adminwidgets

class inputTimeForm(forms.ModelForm):
    class Meta:
        model = Hours
        widgets = {
            'date':adminwidgets.AdminDateWidget(),
            'volunteer_site':forms.HiddenInput(),
            }
        
class NewSiteForm(forms.ModelForm):
    class Meta:
        model = Site
    job_description = forms.CharField(widget=forms.Textarea(attrs={'rows':3}), required=True)

class ExistingSiteForm(forms.ModelForm):
    class Meta:
        model = VolunteerSite
        fields = ['site','job_description']
        widgets = {'job_description':forms.Textarea(attrs={'rows':3})}
        
class SupervisorForm(forms.ModelForm):
    class Meta:
        model = SiteSupervisor
        exclude = ['site']
    
class SelectSupervisorForm(forms.Form):    
    select_existing = forms.ModelChoiceField(SiteSupervisor.objects.all(), required=False)
    
