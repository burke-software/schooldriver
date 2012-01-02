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
from tempfile import mkstemp
from ajax_filtered_fields.forms import ManyToManyByRelatedField

from ecwsp.sis.models import *
from ecwsp.schedule.models import *
from ecwsp.administration.models import * 

class CohortForm(forms.ModelForm):
    class Meta:
        model = Cohort
    class Media:
        js = (
            settings.ADMIN_MEDIA_PREFIX + "js/SelectBox.js",
            settings.ADMIN_MEDIA_PREFIX + "js/SelectFilter2.js",
            '/static/js/jquery.js',
            '/static/js/ajax_filtered_fields.js',
        )
    students = ManyToManyByRelatedField(Student, 'year', include_blank=False)

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
    
    ssn = USSocialSecurityNumberField(required=False)
    state = USStateField()
    zip = USZipCodeField(required=False)
    siblings = AutoCompleteSelectMultipleField('all_student', required=False)
    emergency_contacts = AutoCompleteSelectMultipleField('emergency_contact', required=False)


class UserPreferenceForm(forms.ModelForm):
    class Meta:
        model = UserPreference
        widgets = {
            'additional_report_fields': forms.CheckboxSelectMultiple,
        }


class DeletedStudentLookupForm(forms.Form):
    student = AutoCompleteSelectField('deleted_student')


class StudentLookupForm(forms.Form):
    student = AutoCompleteSelectField('dstudent')


class UploadFileForm(forms.Form):
    file  = forms.FileField()
    
class UploadNaviance(forms.Form):
    import_file = forms.FileField()
    test = forms.ModelChoiceField(queryset=StandardTest.objects.all())
    
class UploadStandardTestResultForm(UploadFileForm):
    test = forms.ModelChoiceField(queryset=StandardTest.objects.all())


class StudentAttendanceForm(forms.ModelForm):
    class Meta:
        model = StudentAttendance
        widgets = {
            'student': forms.HiddenInput(attrs={'tabindex':"-1", 'class':'student_select', 'onfocus':"this.defaultIndex=this.selectedIndex;", 'onchange':"this.selectedIndex=this.defaultIndex;"}),
            'date': forms.HiddenInput(),
            'notes': forms.TextInput(attrs={'tabindex':"-1",}),
        }
    status = forms.ModelChoiceField(widget=forms.Select(attrs={'class':'status',}), queryset=AttendanceStatus.objects.filter(teacher_selectable=True))


class ASPAttendanceForm(forms.ModelForm):
    class Meta:
        model = StudentAttendance
        widgets = {
            'student': forms.HiddenInput(attrs={'tabindex':"-1", 'class':'student_select', 'onfocus':"this.defaultIndex=this.selectedIndex;", 'onchange':"this.selectedIndex=this.defaultIndex;"}),
            'date': forms.HiddenInput(),
            'course': forms.HiddenInput(),
            'notes': forms.TextInput(attrs={'tabindex':"-1",}),
            'status': forms.Select(attrs={'class':'status',}),
        }

class MarkingPeriodForm(forms.Form):
    marking_period = forms.ModelMultipleChoiceField(queryset=MarkingPeriod.objects.all())

class TimeBasedForm(forms.Form):
    """A generic template for time and school year based forms"""
    this_year = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'onclick':'toggle("id_this_year")'}))
    all_years = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'onclick':'toggle("id_all_years")'}))
    date_begin = forms.DateField(widget=adminwidgets.AdminDateWidget(), required=False)
    date_end = forms.DateField(widget=adminwidgets.AdminDateWidget(), required=False)
    marking_period = forms.ModelMultipleChoiceField(required=False, queryset=MarkingPeriod.objects.all())
    include_deleted = forms.BooleanField(required=False)
    
    class Media:
        js = ('/static/js/time_actions.js',)
        
    def clean(self):
        data = self.cleaned_data
        if not data.get("this_year") and not data.get("all_years"):
            if not data.get("date_begin") or not data.get("date_end"):
                raise forms.ValidationError("You must select this year, all years, or specify a date.")
        return data
    
    def get_dates(self):
        """ Returns begining and start dates in a tuple
        Pass it form.cleaned_data """
        data = self.cleaned_data
        if data['this_year'] and not data['marking_period']:
            start = SchoolYear.objects.get(active_year=True).start_date
            end = SchoolYear.objects.get(active_year=True).end_date
        elif not data['this_year'] and not data['all_years']:
            start = data['date_begin']
            end = data['date_end']
        elif data['marking_period']:
            start = data['marking_period'].all().order_by('start_date')[0].start_date
            end = data['marking_period'].all().order_by('-end_date')[0].end_date
        return (start, end)

class StudentSelectForm(TimeBasedForm):
    """ Generic student selection form."""
    all_students = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'onclick':''}))
    student = AutoCompleteSelectMultipleField('student', required=False)
    sort_by = forms.ChoiceField(choices=(('lname', 'Student last name'), ('year', 'School year'), ('cohort', 'Primary Cohort')), initial=1)
    filter_year = forms.ModelMultipleChoiceField(required=False, queryset=GradeLevel.objects.all())
    filter_cohort = forms.ModelMultipleChoiceField(required=False, queryset=Cohort.objects.all())
    
    def get_template(self, request):
        if self.cleaned_data['template']:
            # use selected template
            template = self.cleaned_data['template']
            return template.file.path
        else:
            # or use uploaded template, saving it to temp file
            template = request.FILES['upload_template']
            tmpfile = mkstemp()[1]
            f = open(tmpfile, 'wb')
            f.write(template.read())
            f.close()
            return tmpfile
    
    def get_students(self, options, worker=False):
        """ Returns all students based on criteria. data should be form.cleaned_data """
        if worker:
            from ecwsp.work_study.models import StudentWorker
            students = StudentWorker.objects.all()
        else:
            students = Student.objects.all()
        
        # if selecting individual students, don't filter out deleted
        # why? Because it's unintuitive to pick one student, forgot about "include
        # deleted" and hit go to recieve a blank sheet.
        if not options['all_students']:
            students = students.filter(id__in=options['student'])
        elif not options['include_deleted']:
            students = students.filter(inactive=False)
        
        if options['student'].count == 1:
            data['student'] = options['student'][0]
            
        if options['sort_by'] == "year":
            students = students.order_by('year', 'lname', 'fname')
        elif options['sort_by'] == "cohort":  
            students = students.order_by('cache_cohort', 'lname', 'fname')
        
        if options['filter_year']:
            students = students.filter(year__in=options['filter_year'])
        
        if options['filter_cohort']:
            students = students.filter(cohorts__in=options['filter_cohort'])
        
        return students


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


class AttendanceBulkChangeForm(forms.Form):
    date = forms.DateField(widget=adminwidgets.AdminDateWidget(), required=False)
    status = forms.ModelChoiceField(queryset=AttendanceStatus.objects.all(), required=False)
    notes  = forms.CharField(max_length=255, required=False)
    private_notes  = forms.CharField(max_length=255, required=False)


class StudentBulkChangeForm(forms.Form):
    grad_date = forms.DateField(widget=adminwidgets.AdminDateWidget(), required=False)
    year = forms.ModelChoiceField(queryset=GradeLevel.objects.all(), required=False)
    individual_education_program = forms.NullBooleanField(required=False)
    cohort = forms.ModelChoiceField(queryset=Cohort.objects.all(), required=False)
    cohort_primary = forms.BooleanField(required=False)
    award = forms.ModelChoiceField(queryset=Award.objects.all(), required=False)
    award_marking_period = forms.ModelChoiceField(queryset=MarkingPeriod.objects.all(), required=False)


class AttendanceDailyForm(forms.Form):
    date = forms.DateField(widget=adminwidgets.AdminDateWidget(), initial=date.today)
    include_private_notes = forms.BooleanField(required=False)


class StudentReportWriterForm(StudentSelectForm):
    template = forms.ModelChoiceField(required=False, queryset=Template.objects.all())
    upload_template = forms.FileField(required=False, help_text="You may choose a template or upload one here")
    
    def clean(self):
        data = super(StudentReportWriterForm, self).clean()
        if not data.get('student') and not data.get('all_students'):
            raise forms.ValidationError("You must either check \"all students\" or select a student")
        if not data.get('template') and not data.get('upload_template'):
            raise forms.ValidationError("You must either select a template or upload one.")
        return data

class StudentGradeReportWriterForm(forms.Form):
    date = forms.DateField(widget=adminwidgets.AdminDateWidget(), initial=date.today)
    template = forms.ModelChoiceField(required=False, queryset=Template.objects.all())
    upload_template = forms.FileField(required=False, help_text="You may choose a template or upload one here")
    include_deleted = forms.BooleanField(required=False)
    all_students = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'onclick':''}))
    student = AutoCompleteSelectMultipleField('student', required=False)
    sort_by = forms.ChoiceField(choices=(('lname', 'Student last name'), ('year', 'School year'), ('cohort', 'Primary Cohort')), initial=1)
    filter_year = forms.ModelMultipleChoiceField(required=False, queryset=GradeLevel.objects.all())
    filter_cohort = forms.ModelMultipleChoiceField(required=False, queryset=Cohort.objects.all())
    
    def clean(self):
        data = super(StudentGradeReportWriterForm, self).clean()
        if not data.get('student') and not data.get('all_students'):
            raise forms.ValidationError("You must either check \"all students\" or select a student")
        if not data.get('template') and not data.get('upload_template'):
            raise forms.ValidationError("You must either select a template or upload one.")
        return data
    
    def get_students(self, options, worker=False):
        """ Returns all students based on criteria. data should be form.cleaned_data """
        if worker:
            from ecwsp.work_study.models import StudentWorker
            students = StudentWorker.objects.all()
        else:
            students = Student.objects.all()
        
        # if selecting individual students, don't filter out deleted
        # why? Because it's unintuitive to pick one student, forgot about "include
        # deleted" and hit go to recieve a blank sheet.
        if not options['all_students']:
            students = students.filter(id__in=options['student'])
        elif not options['include_deleted']:
            students = students.filter(inactive=False)
        
        if options['student'].count == 1:
            data['student'] = options['student'][0]
            
        if options['sort_by'] == "year":
            students = students.order_by('year', 'lname', 'fname')
        elif options['sort_by'] == "hoomroom":  
            pass
        
        if options['filter_year']:
            students = students.filter(year__in=options['filter_year'])
        
        if options['filter_cohort']:
            students = students.filter(cohorts__in=options['filter_cohort'])
        
        return students