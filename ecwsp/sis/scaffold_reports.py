from scaffold_report.report import ScaffoldReport, scaffold_reports, ReportButton
from scaffold_report.views import ScaffoldReportView
from scaffold_report.fields import SimpleCompareField
from scaffold_report.filters import Filter, DecimalCompareFilter, IntCompareFilter, ModelMultipleChoiceFilter, ModelChoiceFilter
from django import forms
from django.forms.extras.widgets import SelectDateWidget
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.utils import ProgrammingError
from django.conf import settings
from django.db.models import Count, Q, DateField, Max
from constance import config
from ecwsp.administration.models import Template, Configuration
from ecwsp.sis.models import Student, SchoolYear, GradeLevel, Faculty, Cohort
from ecwsp.attendance.models import CourseSectionAttendance, StudentAttendance, AttendanceStatus
from ecwsp.schedule.calendar import Calendar
from ecwsp.schedule.models import MarkingPeriod, Department, CourseMeet, Period, CourseSection, Course, CourseSectionTeacher, CourseEnrollment
from ecwsp.grades.models import Grade
from ecwsp.discipline.models import DisciplineAction, DisciplineActionInstance
import autocomplete_light
import datetime
from decimal import Decimal
from openpyxl.cell import get_column_letter
from django.core.exceptions import ValidationError

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
    # TODO: remove initialization from SchoolDateFilter.get_report_context() once the date fields are reinstated
    #school_year = forms.ModelChoiceField(initial=get_active_year, queryset=SchoolYear.objects.all())
    #marking_periods = forms.ModelMultipleChoiceField(
    #    initial=get_active_marking_periods,
    #    queryset=MarkingPeriod.objects.all())


class SchoolDateFilter(Filter):
    template_name = "sis/scaffold/school_date_filter.html"
    verbose_name = "Change Timeframe"
    form_class = TimeBasedForm
    default = True
    can_add = False
    can_remove = False

    def get_report_context(self, report_context):
        # TODO: remove once TimeBasedForm date fields are restored
        self.form.cleaned_data['school_year'] = get_active_year()
        self.form.cleaned_data['marking_periods'] = MarkingPeriod.objects.filter(
            active=True,
            school_year=self.form.cleaned_data['school_year']
        )
        return self.form.cleaned_data

    def get_template_context(self):
        context = super(SchoolDateFilter, self).get_template_context()
        context['year'] = SchoolYear.objects.get(active_year=True)
        return context


def django_to_sql_compare(compare):
    """ Convert django syntax (lte) to sql (<=) """
    compare_sql = '='
    if compare == 'lt':
        compare_sql = '<'
    elif compare == 'lte':
        compare_sql = '<='
    elif compare == 'gt':
        compare_sql = '>'
    elif compare == 'gte':
        compare_sql = '>='
    return compare_sql


class TardyFilter(IntCompareFilter):
    compare_field_string = "tardy_count"
    add_fields = ['tardy_count']

    def queryset_filter(self, queryset, report_context=None, **kwargs):
        date_begin = report_context['date_begin']
        date_end = report_context['date_end']
        compare = self.cleaned_data['field_0']
        value = self.cleaned_data['field_1']

        compare_sql = django_to_sql_compare(compare)

        sql = """select coalesce(count(*), 0) from attendance_studentattendance
                    left join attendance_attendancestatus
                    on attendance_attendancestatus.id = attendance_studentattendance.status_id
                    where attendance_attendancestatus.tardy = True
                    and attendance_studentattendance.student_id = sis_student.user_ptr_id
                    and attendance_studentattendance.date between %s and %s"""
        queryset = queryset.extra(
                select = {'tardy_count': sql },
                select_params = (date_begin, date_end,),
                where = ['(' + sql + ') ' + compare_sql + ' %s'],
                params = (date_begin, date_end, value))
        return queryset


class AbsenceFilter(IntCompareFilter):
    compare_field_string = "absence_count"
    add_fields = ['absence_count']

    def queryset_filter(self, queryset, report_context=None, **kwargs):
        date_begin = report_context['date_begin']
        date_end = report_context['date_end']
        compare = self.cleaned_data['field_0']
        value = self.cleaned_data['field_1']

        compare_sql = django_to_sql_compare(compare)

        sql = """select coalesce(count(*), 0) from attendance_studentattendance
                    left join attendance_attendancestatus
                    on attendance_attendancestatus.id = attendance_studentattendance.status_id
                    where attendance_attendancestatus.absent = True
                    and attendance_studentattendance.student_id = sis_student.user_ptr_id
                    and attendance_studentattendance.date between %s and %s"""
        queryset = queryset.extra(
                select = {'absence_count': sql },
                select_params = (date_begin, date_end,),
                where = ['(' + sql + ') ' + compare_sql + ' %s'],
                params = (date_begin, date_end, value))
        return queryset


class CourseSectionsFilter(ModelMultipleChoiceFilter):
    verbose_name = "Course Sections"
    add_fields = ['course_section']
    model = CourseSection
    default = True

    def queryset_filter(self, queryset, report_context=None, **kwargs):
        report_context['course_sections'] = self.cleaned_data['field_0']
        return queryset


class DateFilter(Filter):
    verbose_name = "Date"
    fields = [forms.DateField(widget=SelectDateWidget(years=range(2014, datetime.date.today().year + 1)))]

    def queryset_filter(self, queryset, report_context=None, **kwargs):
        report_context['date'] = self.cleaned_data['field_0']
        return queryset


class StudentsFilter(ModelMultipleChoiceFilter):
    verbose_name = "Select Students"
    model = Student

    def queryset_filter(self, queryset, report_context=None, **kwargs):
        report_context['students'] = self.cleaned_data['field_0']
        return queryset


class ClassPeriodsFilter(ModelMultipleChoiceFilter):
    verbose_name = "Class Periods"
    model = Period

    def queryset_filter(self, queryset, report_context=None, **kwargs):
        report_context['class_periods'] = self.cleaned_data['field_0']
        return queryset


class StudentYearFilter(ModelMultipleChoiceFilter):
    verbose_name="Student Year"
    compare_field_string="year"
    add_fields = ['year']
    model = GradeLevel


class DisciplineForm(forms.Form):
    disc_action = forms.ModelChoiceField(queryset=DisciplineAction.objects.all())
    compare = SimpleCompareField()
    number = forms.IntegerField()


class DisciplineFilter(Filter):
    form_class = DisciplineForm
    add_fields = ['discipline_count']

    def get_add_fields(self):
        disc_action = self.cleaned_data['disc_action']
        return ['discipline_{}_count'.format(disc_action)]

    def queryset_filter(self, queryset, report_context=None, **kwargs):
        date_begin = report_context['date_begin']
        date_end = report_context['date_end']
        disc_action = self.cleaned_data['disc_action']
        compare = self.cleaned_data['compare']
        number = self.cleaned_data['number']

        add_field = self.get_add_fields()[0]
        compare_sql = django_to_sql_compare(compare)

        sql = """select COALESCE(sum(quantity), 0) from discipline_disciplineactioninstance
                    join discipline_disciplineaction
                    on discipline_disciplineaction.id = discipline_disciplineactioninstance.action_id
                    join discipline_studentdiscipline
                    on discipline_studentdiscipline.id = discipline_disciplineactioninstance.student_discipline_id
                    join discipline_studentdiscipline_students
                    on discipline_studentdiscipline_students.studentdiscipline_id = discipline_studentdiscipline.id
                    where discipline_disciplineaction.id = %s
                    and discipline_studentdiscipline_students.student_id = sis_student.user_ptr_id
                    and discipline_studentdiscipline.date between %s and %s"""
        queryset = queryset.extra(
                select = {add_field: sql },
                select_params = (disc_action.id, date_begin, date_end,),
                where = ['(' + sql + ') ' + compare_sql + ' %s'],
                params = (disc_action.id, date_begin, date_end, number))
        return queryset


class CourseSectionGradeFilter(Filter):
    verbose_name = "Grades (Course Section Final)"
    fields = [
        SimpleCompareField,
        forms.IntegerField(widget=forms.TextInput(attrs={'style': 'width:60px'})),
        forms.IntegerField(required=False, widget=forms.TextInput(attrs={'placeholder': "Every", 'style': 'width:41px'})),
    ]
    post_form_text = 'time(s)'
    add_fields = ['course_section_grade_count']

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
            'courseenrollment__course_section__marking_period__start_date__gte': date_begin,
            'courseenrollment__course_section__course__marking_period__end_date__lte': date_end,
        }

        if times:
            queryset = queryset.filter(**grade_kwarg).annotate(
                course_section_grade_count=Count('courseenrollment', distinct=True)).filter(course_section_grade_count__gte=times)
        else:
            queryset = queryset.exclude(**grade_kwarg).annotate(
                course_section_grade_count=Count('courseenrollment', distinct=True))
        return queryset


class MpAvgGradeFilter(CourseSectionGradeFilter):
    verbose_name = "Grades (Marking Period Average)"
    add_fields = ['mp_avg_grade_count']

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
        queryset = queryset.filter(**grade_kwarg).annotate(
            mp_avg_grade_count=Count('studentmarkingperiodgrade', distinct=True))
        if times:
            queryset = queryset.filter(mp_avg_grade_count__gte=times)
        return queryset


class MpGradeFilter(CourseSectionGradeFilter):
    verbose_name = "Grades (By Marking Period)"
    add_fields = ['mp_grade_count',]

    def queryset_filter(self, queryset, report_context=None, **kwargs):
        date_begin = report_context['date_begin']
        date_end = report_context['date_end']
        compare = self.cleaned_data['field_0']
        number = self.cleaned_data['field_1']
        times = self.cleaned_data['field_2']
        report_context['mp_grade_filter_compare'] = compare
        report_context['mp_grade_filter_number'] = number
        grade_kwarg = {
            'grade__grade__' + compare: number,
            'grade__marking_period__start_date__gte': date_begin,
            'grade__marking_period__end_date__lte': date_end,
            'grade__override_final': False,
        }
        queryset = queryset.filter(**grade_kwarg).annotate(
            mp_grade_count=Count('grade', distinct=True))
        if times:
            queryset = queryset.filter(mp_grade_count__gte=times)
        return queryset


class TemplateSelection(ModelChoiceFilter):
    """ Select a template for an appy report
    May affect what extra context is needed (for report cards and transcripts)
    """
    model = Template
    default = True
    can_add = False
    can_remove = False

    def build_form(self):
        super(TemplateSelection, self).build_form()
        self.form.fields['field_0'].required = False

    def get_report_context(self, report_context):
        return {'template': self.form.cleaned_data['field_0']}

    def queryset_filter(self, queryset, report_context=None, **kwargs):
        return queryset


class IncludeDeleted(Filter):
    fields = [forms.BooleanField(initial=True, required=False)]
    default = True
    can_add = False
    can_remove = False

    def queryset_filter(self, queryset, report_context=None, **kwargs):
        include_deleted = self.cleaned_data['field_0']
        if not include_deleted:
            queryset = queryset.filter(is_active=True)
        return queryset


class CohortFilter(ModelMultipleChoiceFilter):
    model = Cohort
    compare_field_string = "cohorts__id"


class SelectSpecificStudentsForm(forms.Form):
    try:
        select_students = autocomplete_light.MultipleChoiceField('StudentUserAutocomplete', required=False)
    except ProgrammingError:
        pass


class SelectSpecificStudents(ModelMultipleChoiceFilter):
    model = Student
    compare_field_string = "pk"
    default = True
    can_add = False
    can_remove = False

    def build_form(self):
        self.form = SelectSpecificStudentsForm()
        self.form.fields['filter_number'] = forms.IntegerField(widget=forms.HiddenInput())
        # This is a hack to force it to accept these choices, otherwise choices gets set to []
        self.form.fields['select_students'] = autocomplete_light.ModelMultipleChoiceField('StudentUserAutocomplete', required=False)

    def queryset_filter(self, queryset, report_context=None, **kwargs):
        selected = self.cleaned_data['select_students']
        if selected:
            return queryset.filter(pk__in=selected)
        return queryset


class ScheduleDaysFilter(Filter):
    fields = [forms.MultipleChoiceField(required=False, choices=CourseMeet.day_choice,
        help_text='''On applicable reports, only the selected days will be included.
            Hold down "Control", or "Command" on a Mac, to select more than one.''')]
    def queryset_filter(self, queryset, report_context=None, **kwargs):
        report_context['schedule_days'] = self.cleaned_data['field_0']
        return queryset


class OmitSubstitutions(Filter):
    fields = [forms.BooleanField(initial=False, required=False,
        help_text='''On applicable reports, number grades will be shown instead
        of letters or abbreviations.''')]
    def queryset_filter(self, queryset, report_context, **kwargs):
        report_context['omit_substitutions'] = self.cleaned_data['field_0']
        return queryset


class SortCourses(Filter):
    """ Allows sorting the courses on a transcript and other templates """
    verbose_name = "Sort Courses"
    fields = [forms.ChoiceField(
        choices=(
            ('department', 'department'),
            ('marking_period, department', 'marking_period, department'),
            ('marking_period, fullname', 'marking_period, fullname'),
        ),
        help_text="Sort Courses in template reports",
        initial='department',
    )]

    def queryset_filter(self, queryset, report_context=None, **kwargs):
        report_context['sort_courses'] = self.cleaned_data['field_0']
        return queryset


class GPAReportButton(ReportButton):
    name = "gpa_report"
    name_verbose = "GPA per year"

    def get_report(self, report_view, context):
        students = report_view.report.get_queryset()
        titles = ["Student", "9th", "10th", "11th","12th", "Current"]
        data = []
        current_year = SchoolYear.objects.get(active_year = True)
        two_years_ago = (current_year.end_date + datetime.timedelta(weeks=-(2*52))).year
        three_years_ago = (current_year.end_date + datetime.timedelta(weeks=-(3*52))).year
        four_years_ago = (current_year.end_date + datetime.timedelta(weeks=-(4*52))).year
        for student in students:
            row = [str(student)]
            i = 0
            for year_grade in student.studentyeargrade_set.order_by('year__start_date'):
                if year_grade.year == current_year:
                    row.append(year_grade.grade)
                elif year_grade.year == two_years_ago:
                    row.append(year_grade.grade)
                elif year_grade.year == three_years_ago:
                    row.append(year_grade.grade)
                elif year_grade.year == four_years_ago:
                    row.append(year_grade.grade)
                else:
                    row.append('')
                i += 1
            while i < 4:
                row.append('')
                i += 1
            row.append(student.gpa)
            data.append(row)
        return report_view.list_to_xlsx_response(data, 'gpas_by_year', header=titles)


class FailReportButton(ReportButton):
    name = "fail_report"
    name_verbose = "Failing Students"

    def get_report(self, report_view, context):
        marking_periods = report_view.report.report_context['marking_periods']
        # anticipate str(student.year)
        students = Student.objects.select_related('year__name').filter(
            courseenrollment__course_section__marking_period__in=marking_periods
        ).distinct()
        titles = ['']
        departments = Department.objects.filter(
            course__sections__courseenrollment__user__is_active=True
        ).distinct()

        for department in departments:
            titles += [str(department)]
        titles += ['Total', '', 'Username', 'Year','GPA', '', 'Failed course sections']

        passing_grade = float(Configuration.get_or_default('Passing Grade','70').value)

        data = []
        iy=2
        for student in students:
            row = [str(student)]
            ix = 1 # letter A
            # query the database once per student, not once per student per department
            # anticipate calling str() on grade.course_section and grade.marking_period
            student.failed_grades = student.grade_set.select_related(
                'course_section__course__department_id',
                'course_section__name',
                'marking_period__name',
            ).filter(
                override_final=False,
                grade__lt=passing_grade,
                marking_period__in=marking_periods
            ).distinct()
            department_counts = {}
            end_of_row = []
            for grade in student.failed_grades:
                # every failing grade gets dumped out at the end of the row
                end_of_row += [
                    str(grade.course_section),
                    str(grade.marking_period),
                    str(grade.grade)
                ]
                # add one to the failed grade count for this department
                department_counts[grade.course_section.course.department_id] = department_counts.get(
                    grade.course_section.course.department_id, 0) + 1
            for department in departments:
                row += [department_counts.get(department.pk, 0)]
                ix += 1
            row += [
                '=sum(b{0}:{1}{0})'.format(str(iy),get_column_letter(ix)),
                '',
                student.username,
                str(student.year),
                student.gpa,
                '',
                ]
            row += end_of_row
            data += [row]
            iy += 1

        return report_view.list_to_xlsx_response(data, 'fail_report', header=titles)


class AggregateGradeButton(ReportButton):
    name = "aggregate_grade_report"
    name_verbose = "Aggregated teacher grades"

    def get_report(self, report_view, context):
        mps = report_view.report.report_context['marking_periods']
        titles = ["Teacher", "Range", "No. Students", ""]
        for level in GradeLevel.objects.all():
            titles += [str(level), ""]
        data = [titles]
        ranges = [['100', '90'], ['89.99', '80'], ['79.99', '70'], ['69.99', '60'], ['59.99', '50'], ['49.99', '0']]
        letter_ranges = ['P', 'F']
        for teacher in Faculty.objects.filter(coursesection__marking_period__in=mps, is_active=True).distinct():
            data.append([str(teacher)])
            grades = Grade.objects.filter(
                marking_period__in=mps,
                course_section__teachers=teacher,
                student__is_active=True,
                override_final=False,
            ).filter(
                Q(grade__isnull=False) |
                Q(letter_grade__isnull=False)
            )
            teacher_students_no = grades.distinct().count()
            if teacher_students_no:
                for range in ranges:
                    no_students = grades.filter(
                            grade__range=(range[1],range[0]),
                        ).distinct().count()
                    percent = float(no_students) / float(teacher_students_no)
                    percent = ('%.2f' % (percent * 100,)).rstrip('0').rstrip('.') + "%"
                    row = ["", str(range[1]) + " to " + str(range[0]), no_students, percent]
                    for level in GradeLevel.objects.all():
                        no_students = grades.filter(
                                grade__range=(range[1],range[0]),
                                student__year__in=[level],
                            ).distinct().count()
                        level_students_no = grades.filter(
                                student__year__in=[level],
                            ).distinct().count()
                        percent = ""
                        if level_students_no:
                            percent = float(no_students) / float(level_students_no)
                            percent = ('%.2f' % (percent * 100,)).rstrip('0').rstrip('.') + "%"
                        row += [no_students, percent]
                    data.append(row)
                for range in letter_ranges:
                    no_students = grades.filter(
                            letter_grade=range,
                        ).distinct().count()
                    if teacher_students_no:
                        percent = float(no_students) / float(teacher_students_no)
                        percent = ('%.2f' % (percent * 100,)).rstrip('0').rstrip('.') + "%"
                    else:
                        percent = ""
                    row = ["", str(range), no_students, percent]
                    for level in GradeLevel.objects.all():
                        no_students = grades.filter(
                                letter_grade=range,
                                student__year__in=[level],
                            ).distinct().count()
                        level_students_no = grades.filter(
                                student__year__in=[level],
                            ).distinct().count()
                        if level_students_no:
                            percent = float(no_students) / float(level_students_no)
                            percent = ('%.2f' % (percent * 100,)).rstrip('0').rstrip('.') + "%"
                        else:
                            percent = ""
                        row += [no_students, percent]
                    data.append(row)

        report_data = {'teacher_aggregate': data}

        passing = 70
        titles = ['Grade']
        for dept in Department.objects.all():
            titles.append(str(dept))
            titles.append('')
        dept_data = [titles]
        for level in GradeLevel.objects.all():
            row = [str(level)]
            for dept in Department.objects.all():
                fails = Grade.objects.filter(
                    marking_period__in=mps,
                    course_section__course__department=dept,
                    student__is_active=True,
                    student__year__in=[level],   # Shouldn't need __in. Makes no sense at all.
                    grade__lt=passing,
                    override_final=False,
                ).count()
                total = Grade.objects.filter(
                    marking_period__in=mps,
                    course_section__course__department=dept,
                    student__is_active=True,
                    student__year__in=[level],
                    override_final=False,
                ).count()
                if total:
                    percent = float(fails) / float(total)
                else:
                    percent = 0
                percent = ('%.2f' % (percent * 100,)).rstrip('0').rstrip('.')
                row.append(fails)
                row.append(percent)
            dept_data.append(row)

        report_data['class_dept'] = dept_data
        return report_view.list_to_xlsx_response(report_data, 'Aggregate_grade_report')
        
class GradeDistributionByTeacherButton(ReportButton):
    name = "grade_distribution_report"
    name_verbose = "Grade Distribution By Teacher"
    report_data = {'sheet_1': []}
    column_headers = [
        "Teacher name",
        "Course",
        "Cohort name",
        "Average of all students in cohort",
        "Average for all students in cohorts of this class taught by teacher",
        "Average for all students in course (all teachers)",
        "Average for all students taught by teacher (all cohorts and courses)"
        ]
    
    def get_report(self, report_view, context):
        
        for teacher in Faculty.objects.all():
            teacher_data = self.get_teacher_data(teacher)
            self.add_teacher_data_to_report_sheet(teacher_data, "sheet_1")
            if teacher_data['sections']:
                # add blank row only for teachers with data, otherwise we'll
                # have a bunch of blank rows on top of each other!
                self.add_blank_row_to_report_sheet("sheet_1")
            
        return report_view.list_to_xlsx_response(self.report_data, "grade_distribution_report", header=self.column_headers)
        
    def get_teacher_data(self, teacher):
        teacher_data = {
            'teacher_name' : "%s, %s" % (teacher.last_name, teacher.first_name),
            'teacher_avg' : self.get_teacher_average(teacher),
            'sections' : self.get_all_sections_for_teacher(teacher)
        }
        return teacher_data
        
    def get_all_sections_for_teacher(self, teacher):
        all_sections = []
        for section in CourseSection.objects.filter(teachers__in = [teacher], is_active=True):
            all_sections.append(self.get_individual_section_data(section))
        return all_sections
            
    def get_individual_section_data(self, section):
        individual_section_data = {
            'section_avg' : self.get_section_average(section),
            'course_avg' : self.get_course_average(section.course),
            'section_name' : section.name,
            'cohorts' : self.get_cohort_data_for_section(section)
        }
        return individual_section_data
        
    def get_cohort_data_for_section(self, section):
        cohorts = section.cohorts.all()
        cohort_data = []
        for cohort in cohorts:
            cohort_data.append({
                'cohort_name' : cohort.name,
                'cohort_avg' : self.get_cohort_section_average(cohort, section)
            })
        if not cohorts:
            cohort_data.append({
                'cohort_name' : "(no cohorts)",
                'cohort_avg' : ""
            })
        return cohort_data
        
    def add_teacher_data_to_report_sheet(self, teacher_data, sheet_name):
        for section in teacher_data['sections']:
            for cohort in section['cohorts']:
                new_row = [
                    teacher_data['teacher_name'], 
                    section['section_name'], 
                    cohort['cohort_name'],
                    cohort['cohort_avg'], 
                    section['section_avg'], 
                    section['course_avg'], 
                    teacher_data['teacher_avg']
                ]
                self.report_data[sheet_name].append(new_row)
                
    def add_blank_row_to_report_sheet(self, sheet_name):
        self.report_data[sheet_name].append([""])
            
    def get_cohort_section_average(self, cohort, section):
        section_enrollments = CourseEnrollment.objects.filter(course_section=section, user__in=cohort.students.all())
        return self.get_average_grade_from_enrollment_set(section_enrollments)
            
    def get_section_average(self, section):
        section_enrollments = CourseEnrollment.objects.filter(course_section=section)
        return self.get_average_grade_from_enrollment_set(section_enrollments)
    
    def get_course_average(self, course):
        all_sections = CourseSection.objects.filter(course=course)
        all_sections_enrollments = CourseEnrollment.objects.filter(course_section__in=all_sections)
        return self.get_average_grade_from_enrollment_set(all_sections_enrollments)
    
    def get_teacher_average(self, teacher):
        all_sections = CourseSection.objects.filter(teachers__in=[teacher])
        all_sections_enrollments = CourseEnrollment.objects.filter(course_section__in=all_sections)
        return self.get_average_grade_from_enrollment_set(all_sections_enrollments)
        
    def get_average_grade_from_enrollment_set(self, enrollments):
        """ return the average grade for a given set of student enrollments """
        non_null_grade_count = 0
        sum_of_all_grades = Decimal('0.00')
        for enrollment in enrollments:
            if enrollment.numeric_grade is not None:
                non_null_grade_count += 1
                sum_of_all_grades += enrollment.numeric_grade
        if non_null_grade_count > 0:
            average = sum_of_all_grades / non_null_grade_count
            return round(average, 1)
        else:
            return None
            
class AspReportButton(ReportButton):
    name = "asp_report"
    name_verbose = "ASP Report"

    def get_report(self, report_view, context):
        data = report_view.report.report_to_list(report_view.request.user)
        students = report_view.report.get_queryset()
        date_begin = report_view.report.report_context['date_begin']
        date_end = report_view.report.report_context['date_end']
        compare = report_view.report.report_context.get('mp_grade_filter_compare', None)
        number = report_view.report.report_context.get('mp_grade_filter_number', None)
        header = context['headers']

        for i, student in enumerate(students):
            grades = student.grade_set.filter(
                override_final=False,
                marking_period__start_date__gte=date_begin,
                marking_period__end_date__lte=date_end,
                )
            if compare:
                grades = grades.filter(**{'grade__' + compare: number})
                for grade in grades.order_by('course_section__course__department', 'marking_period'):
                    data[i].append('{} {}'.format(grade.marking_period.name, grade.course_section.name))
                    data[i].append(grade.grade)

        return report_view.list_to_xlsx_response(data, 'ASP_Report', header)


class ReportView(ScaffoldReportView):
    template_name = 'sis/scaffold/CourseAttendance.html'


class CourseSectionAttendanceButton(ReportButton):

    name = "course_section_attendance"
    name_verbose = "Generate Report"

    def daily_attendance(self, date, student):
        return StudentAttendance.objects.get(student=student, date=date)

    def daily_course_attendance(self, student, course_section, period, date):
        return CourseSectionAttendance.objects.get(course_section=course_section, period=period, date=date, student=student)

    def total_absences(self, student, course_section):
        try:
            status = AttendanceStatus.objects.get(name='Absent')
            total = student.coursesectionattendance_set.filter(course_section=course_section, status=status).count()
            if total == 0:
                return ""
            else:
                return total
        except ObjectDoesNotExist:
            return ""

    def total_tardies(self, student, course_section):
        try:
            status = AttendanceStatus.objects.get(name='Tardy')
            total = student.coursesectionattendance_set.filter(course_section=course_section, status=status).count()
            if total == 0:
                return ""
            else:
                return total
        except ObjectDoesNotExist:
            return ""

    def total_excused_absences(self, student, course_section):
        try:
            status = AttendanceStatus.objects.get(name='Absent Excused')
            total = student.coursesectionattendance_set.filter(course_section=course_section, status=status).count()
            if total == 0:
                return ""
            else:
                return total
        except ObjectDoesNotExist:
            return ""

    def total_excused_tardies(self, student, course_section):
        try:
            status = AttendanceStatus.objects.get(name='Tardy Excused')
            total = student.coursesectionattendance_set.filter(course_section=course_section, status=status).count()
            if total == 0:
                return ""
            else:
                return total
        except ObjectDoesNotExist:
            return ""


    def get_report(self, report_view, context):


        # Get filter info
        data = []
        students = report_view.report.report_context.get('students')
        course_sections = report_view.report.report_context.get('course_sections')
        date = report_view.report.report_context.get('date')

        # Use today as default date if date not chosen
        if not date:
            date = datetime.date.today()

        # Add document name to report
        document_name = 'CourseAttendanceReport_{}.xlsx'.format(date)

        if course_sections:

            for course_section in course_sections:
                course_meets = []
                data.append([""])
                class_periods = report_view.report.report_context.get('class_periods')
                # If user did not use the class_periods filter
                if not class_periods:
                    class_periods = course_section.periods.all()
                for class_period in class_periods:
                    try:
                        course_meet = CourseMeet.objects.get(period=class_period, course_section=course_section,
                                                                   day=date.weekday() + 1)
                    except:
                        break
                    if class_period in course_section.periods.all() and course_meet not in course_meets:
                        course_meets.append(course_meet)
                        # Add course section information
                        row_1 = [course_section.name]
                        data.append(row_1)
                        row_2 = [str(class_period.start_time) + "-" + str(class_period.end_time)]
                        data.append(row_2)
                        row_3 = []
                        for teacher in course_section.teachers.all():
                            row_3.append(str(teacher))
                        data.append(row_3)
                        titles = ["Last Name", "First Name", "First Period", "Notes", "Course Sec.", "Notes",
                        "Time In", "Absences", "Excused Abs.", "Tardies", "Excused Tardies"]
                        data.append(titles)

                        course_attendances = CourseSectionAttendance.objects.filter(course_section=course_section,
                                                                                period=class_period, date=date)
                        for course_attendance in course_attendances:

                            # Add a row for each student
                            row = []
                            student = course_attendance.student
                             # If student filter is not used or
                             # student filter is used and the student is one of the chosen students
                            if not students or students and student in students:
                                row.append(student.last_name)
                                row.append(student.first_name)
                                try:
                                    daily_attendance = self.daily_attendance(date, student)
                                    row.append(str(daily_attendance.status))
                                    row.append(daily_attendance.notes)
                                except:
                                    row.append("")
                                    row.append("")
                                try:
                                    attendance = self.daily_course_attendance(student, course_section, class_period, date)
                                    row.append(str(attendance.status))
                                    row.append(attendance.notes)
                                except:
                                    row.append("")
                                    row.append("")
                                row.append(course_attendance.time_in)
                                row.append(self.total_absences(student, course_section))
                                row.append(self.total_excused_absences(student, course_section))
                                row.append(self.total_tardies(student, course_section))
                                row.append(self.total_excused_tardies(student, course_section))
                                data.append(row)

        else:
            data = []

        return report_view.list_to_xlsx_response(data, document_name)

def strip_trailing_zeros(x):
    x = str(x).strip()
    # http://stackoverflow.com/a/2440786
    return x.rstrip('0').rstrip('.')


class struct(object):
    def __unicode__(self):
        return ""


class SisReport(ScaffoldReport):
    name = "student_report"
    model = Student
    preview_fields = ['first_name', 'last_name']
    permissions_required = ['sis.reports']
    filters = (
        SortCourses(),
        SchoolDateFilter(),
        DecimalCompareFilter(verbose_name="Filter by GPA", compare_field_string="cached_gpa", add_fields=('gpa',)),
        AbsenceFilter(),
        TardyFilter(verbose_name="Tardies"),
        DisciplineFilter(),
        StudentYearFilter(),
        SelectSpecificStudents(),
        CohortFilter(),
        MpAvgGradeFilter(),
        MpGradeFilter(),
        CourseSectionGradeFilter(),
        TemplateSelection(),
        IncludeDeleted(),
        ScheduleDaysFilter(),
        OmitSubstitutions(),
    )
    report_buttons = (
        AspReportButton(),
        AggregateGradeButton(),
        FailReportButton(),
        GPAReportButton(),
        GradeDistributionByTeacherButton(),
    )

    def is_passing(self, grade):
        """ Is a grade considered passing """
        try:
            if float(grade) >= self.pass_score:
                return True
        except:
            pass
        if grade in self.pass_letters.split(','):
            return True
        return False

    def get_student_report_card_data(self, student):
        course_sections = student.coursesection_set.filter(
            course__graded=True,
            marking_period__in=self.marking_periods,
        ).distinct().order_by('course__department')
        marking_periods = self.marking_periods.order_by('start_date')
        mp_grade = {}
        for marking_period in marking_periods:
            smpg = student.studentmarkingperiodgrade_set.filter(marking_period=marking_period).first()
            marking_period.smpg = smpg
            # also save to a dict for alternative lookup
            mp_grade[marking_period.name] = smpg
        student.mps = list(marking_periods)
        student.year_grade = student.studentyeargrade_set.filter(year=self.school_year).first()

        # for example: student.mp_grade['1st'] or ...['S1X']
        student.mp_grade = mp_grade

        # the tuples of semester 1 marking periods and semester 2 marking
        # periods are useful for certain calculations
        num_mps = len(student.mps)
        semester_1_mps = student.mps[:num_mps/2]
        student.semester_1_mps = tuple([int(x.id) for x in semester_1_mps])

        semester_2_mps = student.mps[num_mps/2:]
        student.semester_2_mps = tuple([int(x.id) for x in semester_2_mps])

        # inject this function for use by reports that specifically request it
        # not calculating here as it may create errors for schools that don't
        # actually need this function...
        student.semester_average = Grade.get_scaled_multiple_mp_average

        for course_section in course_sections:
            course_enrollment = course_section.courseenrollment_set.get(user=student)
            grades = course_section.grade_set.filter(student=student).filter(
                marking_period__isnull=False,
                marking_period__show_reports=True).order_by('marking_period__start_date')

            section_mp_grades = {}
            for i, marking_period in enumerate(self.marking_periods.order_by('start_date')):
                for grade in grades:
                    if grade.marking_period_id == marking_period.id:
                        # course_section.grade1, course_section.grade2, etc
                        setattr(course_section, "grade" + str(i + 1), grade)

                        # also save grade in a dict; fetched by MP name
                        # useful if mp.id is in unexpected order
                        # i.e. course_section.mp_grade['S1X']
                        section_mp_grades[marking_period.name] = grade
                        break
                attr_name = "grade" + str(i + 1)
                if not hasattr(course_section, attr_name):
                    setattr(course_section, attr_name, self.blank_grade)

                if marking_period.name not in section_mp_grades:
                    # populate the dict with blank grade
                    section_mp_grades[marking_period.name] = self.blank_grade

                # set the mp_grades dict to the course_section object
                setattr(course_section, 'mp_grade', section_mp_grades)
            course_section.final = course_enrollment.grade
            course_section.ce = course_enrollment
        student.course_sections = course_sections
        student.courses = student.course_sections  # Backwards compatibility

        #Attendance for marking period
        i = 1
        student.absent_total = 0
        student.absent_unexcused_total = 0
        student.tardy_total = 0
        student.tardy_unexcused_total = 0
        student.dismissed_total = 0
        for mp in self.marking_periods.order_by('start_date'):
            absent = student.student_attn.filter(status__absent=True, date__range=(mp.start_date, mp.end_date))
            tardy = student.student_attn.filter(status__tardy=True, date__range=(mp.start_date, mp.end_date))
            dismissed = student.student_attn.filter(status__code="D", date__range=(mp.start_date, mp.end_date)).count()
            absent_unexcused = absent.exclude(status__excused=True).count()
            tardy_unexcused = tardy.exclude(status__excused=True).count()
            absent = absent.count()
            tardy = tardy.count()

            student.absent_total += absent
            student.tardy_total += tardy
            student.absent_unexcused_total += absent_unexcused
            student.tardy_unexcused_total += tardy_unexcused
            student.dismissed_total += dismissed
            setattr(student, "absent" + str(i), absent)
            setattr(student, "tardy" + str(i), tardy)
            setattr(student, "tardy_unexcused" + str(i), tardy_unexcused)
            setattr(student, "absent_unexcused" + str(i), absent_unexcused)
            setattr(student, "dismissed" + str(i), dismissed)
            i += 1
        while i <= 6:
            setattr(student, "absent" + str(i), "")
            setattr(student, "tardy" + str(i), "")
            setattr(student, "tardy_unexcused" + str(i), "")
            setattr(student, "absent_unexcused" + str(i), "")
            setattr(student, "dismissed" + str(i), "")
            i += 1

    def get_student_transcript_data(self, student):
        show_incomplete_without_grade = config.TRANSCRIPT_SHOW_INCOMPLETE_COURSES_WITHOUT_GRADE
        def fake_method(*args, **kargs): return ''
        student.years = SchoolYear.objects.filter(
            markingperiod__show_reports=True,
            markingperiod__coursesection__courseenrollment__user=student,
            ).exclude(omityeargpa__student=student).distinct().order_by('start_date')
        if show_incomplete_without_grade is False:
            # The school doesn't want to show all grades (default)
            student.years = student.years.filter(start_date__lt=self.date_end)
        for year in student.years:
            if show_incomplete_without_grade is True and year.start_date > self.date_end:
                year.hide_grades = True
            else:
                year.hide_grades = False
            year.credits = 0
            year.possible_credits = 0
            year.mps = MarkingPeriod.objects.filter(coursesection__courseenrollment__user=student, school_year=year, show_reports=True).distinct().order_by("start_date")
            i = 1
            for mp in year.mps:
                setattr(year, "mp" + str(i), mp.shortname)
                i += 1
            while i <= 6:
                setattr(year, "mp" + str(i), "")
                i += 1
            year.course_sections = student.coursesection_set.filter(
                course__graded=True,
                marking_period__school_year=year,
                marking_period__show_reports=True
            ).distinct()
            if self.report_context.get('sort_courses') == 'marking_period, department':
                year.course_sections = year.course_sections.annotate(Count('marking_period'), Max('marking_period__end_date')).order_by('-marking_period__count', 'marking_period__end_date__max', 'course__department')
            if self.report_context.get('sort_courses') == 'marking_period, fullname':
                year.course_sections = year.course_sections.annotate(Count('marking_period'), Max('marking_period__end_date')).order_by('-marking_period__count', 'marking_period__end_date__max', 'course__fullname')
            else:
                year.course_sections = year.course_sections.order_by('course__department')
            year_grades = student.grade_set.filter(marking_period__show_reports=True, marking_period__end_date__lte=self.report_context['date_end'])
            year.year_grade = student.studentyeargrade_set.filter(year=year).first()
            if year.hide_grades is True:
                year.year_grade.get_grade = fake_method
            # course section grades
            for course_section in year.course_sections:
                course_enrollment = course_section.courseenrollment_set.get(user=student)
                if year.hide_grades is True:
                    # Hide the grades for the transcript.
                    course_enrollment.get_grade = fake_method
                course_section.ce = course_enrollment
                # Grades
                course_section_grades = year_grades.filter(course_section=course_section).distinct()
                i = 1
                if year.hide_grades is False:
                    for mp in year.mps:
                        if mp not in course_section.marking_period.all():
                            # Obey the registrar! Don't include grades from marking periods when the course section didn't meet.
                            setattr(course_section, "grade" + str(i), "")
                            i += 1
                            continue
                        # We can't overwrite cells, so we have to get seperate variables for each mp grade.
                        try:
                            grade = course_section_grades.get(marking_period=mp).get_grade(
                                number=self.report_context.get('omit_substitutions'))
                            grade = " " + str(grade) + " "
                        except:
                            grade = ""
                        setattr(course_section, "grade" + str(i), grade)
                        i += 1
                while i <= 6:
                    setattr(course_section, "grade" + str(i), "")
                    i += 1
                course_section.final = course_enrollment.get_grade(self.date_end)

                if course_section.course.course_type.award_credits:
                    if self.is_passing(course_section.final):
                        year.credits += course_section.credits
                    if course_section.credits:
                        year.possible_credits += course_section.credits

            year.courses = year.course_sections  # Backwards template compatibility

            # Averages per marking period
            i = 1
            for mp in year.mps:
                if mp.end_date <= self.report_context['date_end']:
                    mp_grade = student.studentmarkingperiodgrade_set.get(marking_period=mp)
                    setattr(year, 'mp' + str(i) + 'ave', mp_grade.grade)
                    i += 1
            while i <= 6:
                setattr(year, 'mp' + str(i) + 'ave', "")
                i += 1

            if self.date_end >= year.end_date:
                year.ave = student.studentyeargrade_set.get(year=year).grade
            else:
                year.ave = student.studentyeargrade_set.get(year=year).get_grade(date_report=self.date_end)

            # Attendance for year
            if not hasattr(self, 'year_days'):
                self.year_days = {}
            if not year.id in self.year_days:
                self.year_days[year.id] = year.get_number_days()
            year.total_days = self.year_days[year.id]
            year.nonmemb = student.student_attn.filter(status__code="nonmemb", date__range=(year.start_date, year.end_date)).count()
            year.absent = student.student_attn.filter(status__absent=True, date__range=(year.start_date, year.end_date)).count()
            year.tardy = student.student_attn.filter(status__tardy=True, date__range=(year.start_date, year.end_date)).count()
            year.dismissed = student.student_attn.filter(status__code="D", date__range=(year.start_date, year.end_date)).count()
            # credits per dept
            student.departments = Department.objects.filter(
                course__sections__courseenrollment__user=student,
                course__course_type__award_credits=True,
            ).distinct()
            student.departments_text = ""
            for dept in student.departments:
                c = 0
                for course_section in student.coursesection_set.filter(
                    course__department=dept,
                    marking_period__school_year__end_date__lte=self.date_end,
                    course__graded=True).distinct():
                    if course_section.course.course_type.award_credits and course_section.course.credits and self.is_passing(
                        course_section.courseenrollment_set.get(user=student).grade
                    ):
                        c += course_section.credits
                dept.credits = c
                student.departments_text += "| %s: %s " % (dept, dept.credits)
            student.departments_text += "|"

            # Standardized tests
            if 'ecwsp.standard_test' in settings.INSTALLED_APPS:
                from ecwsp.standard_test.models import StandardTest
                student.tests = []
                student.highest_tests = []
                for test_result in student.standardtestresult_set.filter(
                    test__show_on_reports=True,
                    show_on_reports=True
                    ).order_by('test'):
                    test_result.categories = ""
                    for cat in test_result.standardcategorygrade_set.filter(category__is_total=False):
                        test_result.categories += '%s: %s | ' % (cat.category.name, strip_trailing_zeros(cat.grade))
                    test_result.categories = test_result.categories [:-3]
                    student.tests.append(test_result)

                for test in StandardTest.objects.filter(standardtestresult__student=student, show_on_reports=True, standardtestresult__show_on_reports=True).distinct():
                    test.total = strip_trailing_zeros(test.get_cherry_pick_total(student))
                    student.highest_tests.append(test)

    def get_appy_template(self):
        return self.report_context.get('template').file

    def get_appy_context(self):
        context = super(SisReport, self).get_appy_context()
        context['date'] = datetime.date.today()
        # Need this to override student_queryset on special reports
        if hasattr(self, 'student_queryset'):
            students = self.student_queryset
            context['objects'] = students
        else:
            students = context['objects']
        template = self.report_context.get('template')
        if template:
            # TODO: Change to date_end?
            self.for_date = self.report_context['date_begin']
            self.date_end = self.report_context['date_end']

            # backwards compatibility for templates
            context['date_begin'] = self.for_date
            context['date_of_report'] = self.date_end
            context['date_end'] = self.date_end
            context['long_date'] = unicode(datetime.date.today().strftime('%B %d, %Y'))
            context['school_year'] = self.report_context['school_year']
            context['school_name'] = config.SCHOOL_NAME

            if template.transcript:
                self.pass_score = float(Configuration.get_or_default("Passing Grade", '70').value)
                self.pass_letters = Configuration.get_or_default("Letter Passing Grade", 'A,B,C,P').value
                for student in students:
                    self.get_student_transcript_data(student)
            if template.benchmark_report_card and \
                'ecwsp.benchmark_grade' in settings.INSTALLED_APPS:
                from ecwsp.benchmark_grade.report import get_benchmark_report_card_data
                get_benchmark_report_card_data(self.report_context, context, students)
            elif template.report_card:
                self.blank_grade = Grade()
                school_year = SchoolYear.objects.filter(start_date__lte=self.report_context['date_end']
                        ).order_by('-start_date').first()
                self.school_year = school_year
                context['year'] = school_year
                self.marking_periods = MarkingPeriod.objects.filter(
                    school_year=school_year, show_reports=True)
                context['marking_periods'] = self.marking_periods.order_by('start_date')
                for student in students:
                    self.get_student_report_card_data(student)
            if template.general_student:
                cal = Calendar()
                schedule_days = self.report_context.get('schedule_days', None)
                
                # If either the start date or end date of a MP is 
                # within the requested time period, we want that MP
                marking_periods = MarkingPeriod.objects.filter(
                    Q(
                        end_date__gte=self.report_context['date_begin'],
                        end_date__lte=self.report_context['date_end']
                    ) | 
                    Q(
                        start_date__gte=self.report_context['date_begin'],
                        start_date__lte=self.report_context['date_end']
                    )).order_by('start_date')
                
                if not marking_periods.count():
                    marking_periods = MarkingPeriod.objects.filter(start_date__gte=self.report_context['date_begin']).order_by('start_date')
                context['marking_periods'] = ', '.join(marking_periods.values_list('shortname',flat=True))
                context['school_year'] = marking_periods[0].school_year

                current_mp = marking_periods.first()
                context['current_mp'] = current_mp
                for student in students:
                    if current_mp:
                        student.schedule_days, student.periods = cal.build_schedule(student, current_mp,
                            schedule_days=schedule_days)
                    student.discipline_records = student.studentdiscipline_set.filter(date__gte=self.for_date,                                                                 date__lte=self.date_end)
                    records = student.discipline_records
                    for record in records:
                        record.actions = '; '.join(record.action.values_list('name', flat=True))
        context['students'] = students
        return context


class AttendanceReport(ScaffoldReport):

    name = 'attendance_report'
    model = CourseSectionAttendance

    filters = (
        CourseSectionsFilter(),
        DateFilter(),
        StudentsFilter(),
        ClassPeriodsFilter()
    )

    report_buttons = (
        CourseSectionAttendanceButton(),
    )


scaffold_reports.register('student_report', SisReport)
scaffold_reports.register('attendance_report', AttendanceReport)
