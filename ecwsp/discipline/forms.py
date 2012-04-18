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
from ecwsp.administration.models import Configuration
from models import *
import datetime

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
    
def get_start_date_default():
    """ Return default date for report. It should be X work days ago. """
    work_days = (0,1,2,3,4) # python day of weeks mon-fri
    # Traverse back these many days
    days_back = int(Configuration.get_or_default('Discipline Merit Default Days', default=14).value)
    default_date = datetime.date.today()
    while days_back > 0:
        while not default_date.weekday() in work_days:
            default_date = default_date - datetime.timedelta(days=1)
        default_date = default_date - datetime.timedelta(days=1)
        days_back -= 1
    return default_date
def get_default_one():
    return int(Configuration.get_or_default('Discipline Merit Level One', default=0).value)
def get_default_two():
    return int(Configuration.get_or_default('Discipline Merit Level Two', default=1).value)
def get_default_three():
    return int(Configuration.get_or_default('Discipline Merit Level Three', default=3).value)
def get_default_four():
    return int(Configuration.get_or_default('Discipline Merit Level Four', default=5).value)
class MeritForm(forms.Form):
    start_date = forms.DateField(initial=get_start_date_default, widget=adminwidgets.AdminDateWidget())
    end_date = forms.DateField(initial=datetime.date.today, widget=adminwidgets.AdminDateWidget())
    level_one = forms.IntegerField(initial=get_default_one)
    level_two = forms.IntegerField(initial=get_default_two, required=False)
    level_three = forms.IntegerField(initial=get_default_three, required=False)
    level_four = forms.IntegerField(initial=get_default_four, required=False)
    sort_by = forms.ChoiceField(choices=(('lname', 'Student last name'), ('year', 'School year'), ('cohort', 'Primary Cohort')), initial=1)
    