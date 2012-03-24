#   Copyright 2011 David M Burke
#   Author Callista Goss <calli@burkesoftware.com>
#   
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#     
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#      
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#   MA 02110-1301, USA.

from django import forms
from volunteer_track.models import *
from ajax_select.fields import AutoCompleteSelectField
from django.forms import HiddenInput, ChoiceField
from django.contrib.admin import widgets as adminwidgets

def clean_unique(form, field, exclude_initial=True, 
                 format="The %(field)s %(value)s has already been taken."):
    value = form.cleaned_data.get(field)
    if value:
        qs = form._meta.model._default_manager.filter(**{field:value})
        if exclude_initial and form.initial:
            initial_value = form.initial.get(field)
            qs = qs.exclude(**{field:initial_value})
        if qs.count() > 0:
            raise forms.ValidationError(format % {'field':field, 'value':value})
    return value

class inputTimeForm(forms.ModelForm):
    class Meta:
        model = Hours
        widgets = {
            'date':adminwidgets.AdminDateWidget(),
            }
        exclude = ['volunteer_site']
    def clean_date(self):
        return clean_unique(self, 'date')
        
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
    
