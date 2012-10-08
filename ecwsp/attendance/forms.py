#       Copyright 2012 Burke Software and Consulting LLC
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
from django.contrib.admin import widgets as adminwidgets

from models import *
from ecwsp.sis.forms import TimeBasedForm
from ajax_select.fields import AutoCompleteSelectMultipleField, AutoCompleteSelectField
import datetime

class StudentAttendanceForm(forms.ModelForm):
    class Meta:
        model = StudentAttendance
        widgets = {
            'student': forms.HiddenInput(attrs={'tabindex':"-1", 'class':'student_select', 'onfocus':"this.defaultIndex=this.selectedIndex;", 'onchange':"this.selectedIndex=this.defaultIndex;"}),
            'date': forms.HiddenInput(),
            'notes': forms.TextInput(attrs={'tabindex':"-1",}),
        }
    status = forms.ModelChoiceField(widget=forms.Select(attrs={'class':'status',}), queryset=AttendanceStatus.objects.filter(teacher_selectable=True))
    
    
class CourseAttendanceForm(forms.Form):
    student = forms.ModelChoiceField(queryset=Student.objects.all(), widget=forms.HiddenInput())
    status = forms.ModelChoiceField(
        widget=forms.Select(attrs={'class':'status',}),
        queryset=AttendanceStatus.objects.filter(teacher_selectable=True),
        required=False)

    
class AttendanceReportForm(TimeBasedForm):
    filter_status = forms.ModelChoiceField(required=False, queryset=AttendanceStatus.objects.all())
    filter_count =forms.IntegerField(initial=0, help_text="Minimal number of above needed to show in report")
    filter_total_absences = forms.IntegerField(initial=0, help_text="Minimal number of total absenses needed to show in report")
    filter_total_tardies = forms.IntegerField(initial=0, help_text="Minimal number of total tardies needed to show in report")
    
    
class AttendanceViewForm(forms.Form):
    all_years = forms.BooleanField(required=False, help_text="If check report will contain all student records. Otherwise it will only show current year.")
    order_by = forms.ChoiceField(initial=0, choices=(('Date','Date'),('Status','Status'),))
    include_private_notes = forms.BooleanField(required=False)
    student = AutoCompleteSelectField('attendance_view_student')


class AttendanceDailyForm(forms.Form):
    date = forms.DateField(widget=adminwidgets.AdminDateWidget(), initial=datetime.date.today)
    include_private_notes = forms.BooleanField(required=False)


class AttendanceBulkChangeForm(forms.Form):
    date = forms.DateField(widget=adminwidgets.AdminDateWidget(), required=False)
    status = forms.ModelChoiceField(queryset=AttendanceStatus.objects.all(), required=False)
    notes  = forms.CharField(max_length=255, required=False)
    private_notes  = forms.CharField(max_length=255, required=False)