import floppyforms as forms
from django.contrib.admin import widgets as adminwidgets
from django.contrib import messages
from django.conf import settings

from tempfile import mkstemp

from ecwsp.sis.models import Student, UserPreference, SchoolYear, GradeLevel, Cohort
from ecwsp.schedule.models import MarkingPeriod, CourseMeet, Award
from ecwsp.administration.models import Template
import autocomplete_light

class UserPreferenceForm(forms.ModelForm):
    class Meta:
        model = UserPreference
        widgets = {
            'prefered_file_format': forms.Select,
            'include_deleted_students': forms.CheckboxInput,
            'course_sort': forms.Select,
            'omr_default_point_value': forms.NumberInput,
            'omr_default_save_question_to_bank': forms.CheckboxInput,
            'omr_default_number_answers': forms.NumberInput,
            'gradebook_preference': forms.Select,
        }


class DeletedStudentLookupForm(forms.Form):
    student = autocomplete_light.ChoiceField('StudentUserAutocomplete')


class StudentLookupForm(forms.Form):
    student = autocomplete_light.ChoiceField('StudentActiveUserAutocomplete')
    

class UploadFileForm(forms.Form):
    file  = forms.FileField()

class MarkingPeriodForm(forms.Form):
    marking_period = forms.ModelMultipleChoiceField(queryset=MarkingPeriod.objects.all())

class TimeBasedForm(forms.Form):
    """A generic template for time and school year based forms"""
    this_year = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'onclick':'toggle("id_this_year")'}))
    all_years = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'onclick':'toggle("id_all_years")'}))
    date_begin = forms.DateField(widget=adminwidgets.AdminDateWidget(), required=False, validators=settings.DATE_VALIDATORS)
    date_end = forms.DateField(widget=adminwidgets.AdminDateWidget(), required=False, validators=settings.DATE_VALIDATORS)
    # CourseMeet.day_choice is a tuple of tuples; need the first value from each inner tuple for initial
    schedule_days = forms.MultipleChoiceField(required=False, choices=CourseMeet.day_choice,
        help_text='''On applicable reports, only the selected days will be included.
            Hold down "Control", or "Command" on a Mac, to select more than one.''')
    marking_period = forms.ModelMultipleChoiceField(required=False, queryset=MarkingPeriod.objects.all())
    include_deleted = forms.BooleanField(required=False)
    
    class Media:
        js = ('/static/js/time_actions.js',)
        
    def clean(self):
        data = self.cleaned_data
        if not data.get("this_year") and not data.get("all_years"):
            if not data.get("date_begin") or not data.get("date_end"):
                if not data.get("marking_period"):
                    raise forms.ValidationError("You must select this year, all years, specify a date, or select a marking period.")
        return data
    
    def get_dates(self):
        """ Returns begining and start dates in a tuple
        Pass it form.cleaned_data """
        data = self.cleaned_data
        if data['this_year'] and not data['marking_period']:
            start = SchoolYear.objects.get(active_year=True).start_date
            # if they want a date in the future, let them specify it explicitly
            end = min(date.today(), SchoolYear.objects.get(active_year=True).end_date)
        elif not data['this_year'] and not data['all_years'] and not data['marking_period']:
            start = data['date_begin']
            end = data['date_end']
        elif data['marking_period']:
            start = data['marking_period'].all().order_by('start_date')[0].start_date
            end = data['marking_period'].all().order_by('-end_date')[0].end_date
        else: # all of time
            start = date(1980, 1, 1)
            end = date(2980, 1, 1)
        return (start, end)

class YearSelectForm(forms.Form):
    school_year = forms.ModelChoiceField(queryset=SchoolYear.objects.all())

class StudentSelectForm(TimeBasedForm):
    """ Generic student selection form."""
    all_students = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'onclick':''}))
    student = autocomplete_light.ChoiceField('StudentActiveUserAutocomplete')
    sort_by = forms.ChoiceField(choices=(('last_name', 'Student last name'), ('year', 'School year'), ('cohort', 'Primary Cohort')), initial=1)
    filter_year = forms.ModelMultipleChoiceField(required=False, queryset=GradeLevel.objects.all())
    filter_cohort = forms.ModelMultipleChoiceField(required=False, queryset=Cohort.objects.all())
    
    def get_template(self, request):
        if self.cleaned_data['template']:
            # use selected template
            template = self.cleaned_data['template']
            if template.file:
                return template.file.path
            else:
                messages.error(request, 'Template not found')
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
            students = students.filter(is_active=True)
        
        if options['student'].count == 1:
            data['student'] = options['student'][0]
            
        if options['sort_by'] == "year":
            students = students.order_by('year', 'last_name', 'first_name')
        elif options['sort_by'] == "cohort":  
            students = students.order_by('cache_cohort', 'last_name', 'first_name')
        
        if options['filter_year']:
            students = students.filter(year__in=options['filter_year'])
        
        if options['filter_cohort']:
            students = students.filter(cohorts__in=options['filter_cohort'])
        
        return students


class StudentBulkChangeForm(forms.Form):
    grad_date = forms.DateField(widget=adminwidgets.AdminDateWidget(), required=False, validators=settings.DATE_VALIDATORS)
    year = forms.ModelChoiceField(queryset=GradeLevel.objects.all(), required=False)
    individual_education_program = forms.NullBooleanField(required=False)
    cohort = forms.ModelChoiceField(queryset=Cohort.objects.all(), required=False)
    cohort_primary = forms.BooleanField(required=False)
    award = forms.ModelChoiceField(queryset=Award.objects.all(), required=False)
    award_marking_period = forms.ModelChoiceField(queryset=MarkingPeriod.objects.all(), required=False)


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
