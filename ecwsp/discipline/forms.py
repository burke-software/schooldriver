#       Copyright 2010-2011 Burke Software and Consulting LLC
#       Author David M Burke <david@burkesoftware.com>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 3 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

from django import forms
from django.contrib.localflavor.us.forms import *
from django.contrib.admin import widgets as adminwidgets
from django.conf import settings

from ajax_select.fields import AutoCompleteSelectMultipleField, AutoCompleteSelectField

from ecwsp.sis.forms import TimeBasedForm
from models import *

class DisciplineViewForm(forms.Form):
    student = AutoCompleteSelectField('discipline_view_student')
    
class DisciplineForm(forms.ModelForm):
    class Meta:
        model = StudentDiscipline
        widgets = {
            'comments': forms.TextInput(),
        }
    def add_fields(self, form, index):
        super(DisciplineForm, self).add_fields(form, index)
        form.fields["students"] = AutoCompleteSelectMultipleField('dstudent')
        
class DisciplineStudentStatistics(TimeBasedForm):
    """Form to gather information to be used in a report of discipline issues"""
    order_by = forms.ChoiceField(required=False, choices=(('Student','Student Name'),('Year','Year'),))
    action = forms.ModelChoiceField(required=False, queryset=DisciplineAction.objects.all())
    minimum_action = forms.IntegerField(initial=0, help_text="Minimal number of above action needed to show student in Student Report")
    infraction = forms.ModelChoiceField(required=False, queryset=Infraction.objects.all())
    minimum_infraction = forms.IntegerField(initial=0, help_text="Minimal number of above infraction needed to show student in Student Report")