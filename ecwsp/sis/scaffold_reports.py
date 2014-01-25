from scaffold_report.report import ScaffoldReport, scaffold_reports
from scaffold_report.fields import SimpleCompareField
from scaffold_report.filters import Filter, DecimalCompareFilter, IntCompareFilter, ModelMultipleChoiceFilter
from django import forms
from django.conf import settings
from django.db.models import Count
from ecwsp.sis.models import Student, SchoolYear, GradeLevel
from ecwsp.schedule.models import MarkingPeriod
import datetime

def reverse_compare(compare):
    """ Get the opposite comparison
    greater than becomes less than equals """
    if compare == "gt":
        compare = "lte"
    elif compare == "gte":
        compare = "lt"
    elif compare == "lt":
        compare = "gte"
    elif compare == "lte":
        compare = "gt"
    return compare

def get_active_year():
    return SchoolYear.objects.get(active_year=True)

class TimeBasedForm(forms.Form):
    """A generic template for time and school year based forms"""
    def get_default_start_date():
        return get_active_year().start_date
    def get_default_end_date():
        return get_active_year().end_date
    def get_active_marking_periods():
        return MarkingPeriod.objects.filter(active=True)
    
    date_begin = forms.DateField(initial=get_default_start_date, validators=settings.DATE_VALIDATORS)
    date_end = forms.DateField(initial=get_default_end_date, validators=settings.DATE_VALIDATORS)
    school_year = forms.ModelChoiceField(initial=get_active_year, queryset=SchoolYear.objects.all())
    marking_periods = forms.ModelMultipleChoiceField(
        initial=get_active_marking_periods,
        queryset=MarkingPeriod.objects.all())
    
    
class SchoolDateFilter(Filter):
    template_name = "sis/school_date_filter.html"
    verbose_name = "Change Timeframe"
    form_class = TimeBasedForm
    
    def get_report_context(self, report_context):
        return self.form.cleaned_data
    
    def get_template_context(self):
        context = super(SchoolDateFilter, self).get_template_context()
        context['year'] = SchoolYear.objects.get(active_year=True)
        return context

class TardyFilter(IntCompareFilter):
    compare_field_string = "tardy_count"
    add_fields = ['tardy_count']
    
    def queryset_filter(self, queryset, report_context=None, **kwargs):
        date_begin = report_context['date_begin']
        date_end = report_context['date_end']
        queryset = queryset.filter(
            student_attn__date__range=(date_begin, date_end),
            student_attn__status__tardy=True,
            ).annotate(tardy_count=Count('student_attn', distinct=True))
        queryset = super(TardyFilter, self).queryset_filter(queryset)
        return queryset


class StudentYearFilter(ModelMultipleChoiceFilter):
    verbose_name="Student Year"
    compare_field_string="year"
    add_fields = ['year']
    
    def __init__(self, **kwargs):
        self.queryset = GradeLevel.objects.all()
        return super(StudentYearFilter, self).__init__(**kwargs)
    

class CourseGradeFilter(Filter):
    verbose_name = "Grades (Course Final)"
    fields = [
        SimpleCompareField,
        forms.IntegerField(widget=forms.TextInput(attrs={'style': 'width:60px'})),
        forms.IntegerField(required=False, widget=forms.TextInput(attrs={'placeholder': "Every", 'style': 'width:41px'})),
    ]
    post_form_text = 'time(s)'
    add_fields = ['course_grade_count']
    
    def queryset_filter(self, queryset, report_context=None, **kwargs):
        date_begin = report_context['date_begin']
        date_end = report_context['date_end']
        compare = self.cleaned_data['field_0']
        number = self.cleaned_data['field_1']
        times = self.cleaned_data['field_2']
        
        if not times: # Have to exclude it, which reverses the comparison
            compare = reverse_compare(compare)
        grade_kwarg = {
            'courseenrollment__cached_numeric_grade__' + compare: number,
            'courseenrollment__course__marking_period__start_date__gte': date_begin,
            'courseenrollment__course__marking_period__end_date__lte': date_end,
        }
        
        if times:
            queryset = queryset.filter(**grade_kwarg).annotate(
                course_grade_count=Count('courseenrollment', distinct=True)).filter(course_grade_count__gte=times)
        else: # Every time
            # Produces invalid sql - django bug?
            queryset = queryset.exclude(**grade_kwarg)
        return queryset

class MpGradeFilter(CourseGradeFilter):
    verbose_name = "Grades (MP)"
    add_fields = ['mp_grade_count']
    
    def queryset_filter(self, queryset, report_context=None, **kwargs):
        date_begin = report_context['date_begin']
        date_end = report_context['date_end']
        compare = self.cleaned_data['field_0']
        number = self.cleaned_data['field_1']
        times = self.cleaned_data['field_2']
        grade_kwarg = {
            'studentmarkingperiodgrade__cached_grade__' + compare: number,
            'studentmarkingperiodgrade__marking_period__start_date__gte': date_begin,
            'studentmarkingperiodgrade__marking_period__end_date__lte': date_end,
        }
        if times:
            queryset = queryset.filter(**grade_kwarg).annotate(
                mp_grade_count=Count('studentmarkingperiodgrade', distinct=True)).filter(mp_grade_count__gte=times)
        return queryset


class SisReport(ScaffoldReport):
    name = "student_report"
    model = Student
    filters = (
        DecimalCompareFilter(verbose_name="Filter by GPA", compare_field_string="cache_gpa", add_fields=('gpa',)),
        TardyFilter(verbose_name="Tardies"),
        SchoolDateFilter(),
        StudentYearFilter(),
        MpGradeFilter(),
        CourseGradeFilter(),
    )

scaffold_reports.register('student_report', SisReport)
