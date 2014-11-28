from django import forms
from django.contrib.admin import widgets as adminwidgets
from django.conf import settings
from django.db.utils import ProgrammingError

from models import StudentAttendance, AttendanceStatus
from ecwsp.sis.models import Student
from ecwsp.sis.forms import TimeBasedForm
import datetime
import autocomplete_light


class StudentAttendanceForm(forms.ModelForm):
    class Meta:
        model = StudentAttendance
        widgets = {
            'student': forms.HiddenInput(attrs={'tabindex':"-1", 'class':'student_select', 'onfocus':"this.defaultIndex=this.selectedIndex;", 'onchange':"this.selectedIndex=this.defaultIndex;"}),
            'date': forms.HiddenInput(),
            'notes': forms.TextInput(attrs={'tabindex':"-1",}),
        }
    status = forms.ModelChoiceField(widget=forms.Select(attrs={'class':'status',}), queryset=AttendanceStatus.objects.filter(teacher_selectable=True))


class StudentMultpleAttendanceForm(autocomplete_light.ModelForm):
    """ Form accepts multiple students """
    class Meta:
        model = StudentAttendance
        widgets = {
            'date':  adminwidgets.AdminDateWidget(),
            'time': adminwidgets.AdminTimeWidget(),
        }
        fields = ('date', 'status', 'time', 'notes', 'private_notes')
    student = autocomplete_light.ModelMultipleChoiceField('StudentUserAutocomplete')


class CourseSectionAttendanceForm(forms.Form):
    student = forms.ModelChoiceField(queryset=Student.objects.all(), widget=forms.HiddenInput())
    status = forms.ModelChoiceField(
        widget=forms.Select(attrs={'class':'status',}),
        queryset=AttendanceStatus.objects.filter(teacher_selectable=True),
        required=False)
    time_in = forms.TimeField(required=False, widget=adminwidgets.AdminTimeWidget(attrs={'tabindex':"-1"}))
    notes = forms.CharField(required=False, widget=forms.TextInput(attrs={'tabindex':"-1", 'style': 'width: 150px'}))


class AttendanceReportForm(TimeBasedForm):
    filter_status = forms.ModelChoiceField(required=False, queryset=AttendanceStatus.objects.all())
    filter_count =forms.IntegerField(initial=0, help_text="Minimal number of above needed to show in report")
    filter_total_absences = forms.IntegerField(initial=0, help_text="Minimal number of total absenses needed to show in report")
    filter_total_tardies = forms.IntegerField(initial=0, help_text="Minimal number of total tardies needed to show in report")


class AttendanceViewForm(forms.Form):
    all_years = forms.BooleanField(required=False, help_text="If check report will contain all student records. Otherwise it will only show current year.")
    order_by = forms.ChoiceField(initial=0, choices=(('Date','Date'),('Status','Status'),))
    include_private_notes = forms.BooleanField(required=False)
    try:
        student = autocomplete_light.ModelChoiceField('StudentUserAutocomplete')
    except ProgrammingError:
        pass


class AttendanceDailyForm(forms.Form):
    date = forms.DateField(widget=adminwidgets.AdminDateWidget(), initial=datetime.date.today, validators=settings.DATE_VALIDATORS)
    include_private_notes = forms.BooleanField(required=False)


class AttendanceBulkChangeForm(forms.Form):
    date = forms.DateField(widget=adminwidgets.AdminDateWidget(), required=False, validators=settings.DATE_VALIDATORS)
    status = forms.ModelChoiceField(queryset=AttendanceStatus.objects.all(), required=False)
    notes  = forms.CharField(max_length=255, required=False)
    private_notes  = forms.CharField(max_length=255, required=False)
