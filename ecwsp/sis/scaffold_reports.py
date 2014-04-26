from scaffold_report.report import ScaffoldReport, scaffold_reports, ReportButton
from scaffold_report.fields import SimpleCompareField
from scaffold_report.filters import Filter, DecimalCompareFilter, IntCompareFilter, ModelMultipleChoiceFilter, ModelChoiceFilter
from django import forms
from django.conf import settings
from django.db.models import Count, Q
from ecwsp.administration.models import Template, Configuration
from ecwsp.sis.models import Student, SchoolYear, GradeLevel, Faculty, Cohort
from ecwsp.schedule.calendar import Calendar
from ecwsp.schedule.models import MarkingPeriod, Department, CourseMeet
from ecwsp.grades.models import Grade
from ecwsp.discipline.models import DisciplineAction
import datetime
from decimal import Decimal
from openpyxl.cell import get_column_letter

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
    template_name = "sis/scaffold/school_date_filter.html"
    verbose_name = "Change Timeframe"
    form_class = TimeBasedForm
    default = True
    can_add = False
    can_remove = False

    def get_report_context(self, report_context):
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

        sql = """select coalesce(count(*)) from attendance_studentattendance
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

        sql = """select coalesce(count(*)) from attendance_studentattendance
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


class StudentYearFilter(ModelMultipleChoiceFilter):
    verbose_name="Student Year"
    compare_field_string="year"
    add_fields = ['year']
    model = GradeLevel

class BrendanForm(forms.Form):
    one   = forms.IntegerField(widget=forms.TextInput(attrs={'placeholder': "one"}))
    two   = forms.IntegerField(widget=forms.TextInput(attrs={'placeholder': "two"}))
    three = forms.IntegerField(widget=forms.TextInput(attrs={'placeholder': "three"}))
    four  = forms.IntegerField(widget=forms.TextInput(attrs={'placeholder': "four "}),required=False)
    five  = forms.ChoiceField(required=False)

class BrendanFilter(Filter):
    form_class = BrendanForm

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
        else:
            queryset = queryset.exclude(**grade_kwarg)
        return queryset

class MpAvgGradeFilter(CourseGradeFilter):
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


class MpGradeFilter(CourseGradeFilter):
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
            queryset = queryset.filter(deleted=True)
        return queryset


class CohortFilter(ModelMultipleChoiceFilter):
    model = Cohort
    compare_field_string = "cohorts__id"


from ajax_select.fields import AutoCompleteSelectMultipleField, AutoCompleteSelectField
class SelectSpecificStudentsForm(forms.Form):
    select_students = AutoCompleteSelectMultipleField('dstudent', required=False)

class SelectSpecificStudents(ModelMultipleChoiceFilter):
    model = Student
    compare_field_string = "pk"
    default = True
    can_add = False
    can_remove = False

    def build_form(self):
        self.form = SelectSpecificStudentsForm()
        self.form.fields['filter_number'] = forms.IntegerField(widget=forms.HiddenInput())

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
        students = Student.objects.filter(courseenrollment__course__marking_period__in=marking_periods).distinct()
        titles = ['']
        departments = Department.objects.filter(course__courseenrollment__user__is_active=True).distinct()

        for department in departments:
            titles += [str(department)]
        titles += ['Total', '', 'Username', 'Year','GPA', '', 'Failed courses']

        passing_grade = float(Configuration.get_or_default('Passing Grade','70').value)

        data = []
        iy=3
        for student in students:
            row = [str(student)]
            ix = 1 # letter A
            student.failed_grades = Grade.objects.none()
            for department in departments:
                failed_grades = Grade.objects.filter(override_final=False,course__department=department,course__courseenrollment__user=student,grade__lte=passing_grade,marking_period__in=marking_periods)
                row += [failed_grades.count()]
                student.failed_grades = student.failed_grades | failed_grades
                ix += 1
            row += [
                '=sum(b{0}:{1}{0})'.format(str(iy),get_column_letter(ix)),
                '',
                student.username,
                str(student.year),
                student.gpa,
                '',
                ]
            for grade in student.failed_grades:
                row += [str(grade.course), str(grade.marking_period), str(grade.grade)]
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
        for teacher in Faculty.objects.filter(course__marking_period__in=mps, is_active=True).distinct():
            data.append([str(teacher)])
            grades = Grade.objects.filter(
                marking_period__in=mps,
                course__teacher=teacher,
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
                    course__department=dept,
                    student__is_active=True,
                    student__year__in=[level],   # Shouldn't need __in. Makes no sense at all.
                    grade__lt=passing,
                    override_final=False,
                ).count()
                total = Grade.objects.filter(
                    marking_period__in=mps,
                    course__department=dept,
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
                for grade in grades.order_by('course__department', 'marking_period'):
                    data[i].append('{} {}'.format(grade.marking_period.name, grade.course.shortname))
                    data[i].append(grade.grade)

        return report_view.list_to_xlsx_response(data, 'ASP_Report', header)


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
    filters = (
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
        CourseGradeFilter(),
        TemplateSelection(),
        IncludeDeleted(),
        ScheduleDaysFilter(),
        BrendanFilter(),
    )
    report_buttons = (
        AspReportButton(),
        AggregateGradeButton(),
        FailReportButton(),
        GPAReportButton(),
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
        courses = student.course_set.filter(
            graded=True,
            marking_period__in=self.marking_periods,
        ).distinct().order_by('department')
        for course in courses:
            course_enrollment = course.courseenrollment_set.get(user=student)
            grades = course.grade_set.filter(student=student).filter(
                marking_period__isnull=False,
                marking_period__show_reports=True).order_by('marking_period__start_date')
            i = 1
            for grade in grades:
                # course.grade1, course.grade2, etc
                setattr(course, "grade" + str(i), grade)
                i += 1
            while i <= 4:
                setattr(course, "grade" + str(i), self.blank_grade)
                i += 1
            course.final = course_enrollment.grade
        student.courses = courses

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

    def get_student_transcript_data(self, student, omit_substitutions=False):
        if "ecwsp.benchmark_grade" in settings.INSTALLED_APPS:
            from ecwsp.benchmark_grade.models import Aggregate
            from ecwsp.benchmark_grade.utility import gradebook_get_average, benchmark_find_calculation_rule, gradebook_get_category_average

        student.years = SchoolYear.objects.filter(
            markingperiod__show_reports=True,
            start_date__lt=self.date_end,
            markingperiod__course__courseenrollment__user=student,
            ).exclude(omityeargpa__student=student).distinct().order_by('start_date')
        for year in student.years:
            year.credits = 0
            year.possible_credits = 0
            year.mps = MarkingPeriod.objects.filter(course__courseenrollment__user=student, school_year=year, show_reports=True).distinct().order_by("start_date")
            i = 1
            for mp in year.mps:
                setattr(year, "mp" + str(i), mp.shortname)
                i += 1
            while i <= 6:
                setattr(year, "mp" + str(i), "")
                i += 1
            year.courses = student.course_set.filter(
                graded=True,
                marking_period__school_year=year,
                marking_period__show_reports=True
            ).distinct().order_by('department')
            year_grades = student.grade_set.filter(marking_period__show_reports=True, marking_period__end_date__lte=self.report_context['date_end'])
            # course grades
            for course in year.courses:
                course_enrollment = course.courseenrollment_set.get(user=student)
                # Grades
                course_grades = year_grades.filter(course=course).distinct()
                course_aggregates = None
                if year.benchmark_grade:
                    course_aggregates = Aggregate.objects.filter(course=course, student=student)
                i = 1
                for mp in year.mps:
                    if mp not in course.marking_period.all():
                        # Obey the registrar! Don't include grades from marking periods when the course didn't meet.
                        setattr(course, "grade" + str(i), "")
                        i += 1
                        continue
                    if year.benchmark_grade:
                        setattr(course, "grade" + str(i), gradebook_get_average(student, course, None, mp, omit_substitutions = omit_substitutions))
                    else:
                        # We can't overwrite cells, so we have to get seperate variables for each mp grade.
                        try:
                            grade = course_grades.get(marking_period=mp).get_grade()
                            grade = " " + str(grade) + " "
                        except Grade.DoesNotExist:
                            grade = ""
                        setattr(course, "grade" + str(i), grade)
                    i += 1
                while i <= 6:
                    setattr(course, "grade" + str(i), "")
                    i += 1
                course.final = course_enrollment.grade

                if self.is_passing(course.final):
                    year.credits += course.credits
                if course.credits:
                    year.possible_credits += course.credits

            year.categories_as_courses = []
            if year.benchmark_grade:
                calculation_rule = benchmark_find_calculation_rule(year)
                for category_as_course in calculation_rule.category_as_course_set.filter(include_departments=course.department):
                    i = 1
                    for mp in year.mps:
                        setattr(category_as_course.category, 'grade{}'.format(i), gradebook_get_category_average(student, category_as_course.category, mp))
                        i += 1
                    year.categories_as_courses.append(category_as_course.category)

            # Averages per marking period
            i = 1
            for mp in year.mps:
                if mp.end_date < self.report_context['date_begin']:
                    mp_grade = student.studentmarkingperiodgrade_set.get(marking_period=mp)
                    setattr(year, 'mp' + str(i) + 'ave', mp_grade.grade)
                    i += 1
            while i <= 6:
                setattr(year, 'mp' + str(i) + 'ave', "")
                i += 1

            year.ave = student.studentyeargrade_set.get(year=year).grade

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
            student.departments = Department.objects.filter(course__courseenrollment__user=student).distinct()
            student.departments_text = ""
            for dept in student.departments:
                c = 0
                for course in student.course_set.filter(
                    department=dept,
                    marking_period__school_year__end_date__lte=self.date_end,
                    graded=True).distinct():
                    if course.credits and self.is_passing(course.courseenrollment_set.get(user=student).grade):
                        c += course.credits
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
        return self.report_context.get('template').file.path

    def get_appy_context(self):
        context = super(SisReport, self).get_appy_context()
        context['date'] = datetime.date.today()
        students = context['objects']
        template = self.report_context.get('template')
        if template:
            self.date_end = self.report_context['date_end']
            context['date_of_report'] = self.date_end # backwards compatibility for templates
            if template.transcript:
                self.pass_score = float(Configuration.get_or_default("Passing Grade", '70').value)
                self.pass_letters = Configuration.get_or_default("Letter Passing Grade", 'A,B,C,P').value
                for student in students:
                    self.get_student_transcript_data(student)
            if template.report_card:
                self.blank_grade = struct()
                self.blank_grade.comment = ""
                school_year = SchoolYear.objects.filter(start_date__lte=self.report_context['date_end']
                        ).order_by('-start_date').first()
                context['year'] = school_year
                self.marking_periods = MarkingPeriod.objects.filter(
                    school_year=school_year, show_reports=True)
                context['marking_periods'] = self.marking_periods.order_by('start_date')
                for student in students:
                    self.get_student_report_card_data(student)
            if template.general_student:
                cal = Calendar()
                schedule_days = self.report_context.get('schedule_days', None)
                marking_periods = MarkingPeriod.objects.filter(start_date__gte=self.report_context['date_end'],
                    end_date__lte=self.report_context['date_end']).order_by('start_date')
                if not marking_periods.count():
                    marking_periods = MarkingPeriod.objects.filter(start_date__gte=self.report_context['date_begin']).order_by('start_date')
                current_mp = marking_periods[0]
                for student in students:
                    if current_mp:
                        student.schedule_days, student.periods = cal.build_schedule(student, current_mp,
                            schedule_days=schedule_days)
                    #student.discipline_records = student.studentdiscipline_set.filter(date__gte=begin_end_dates[0],
                    #    date__lte=begin_end_dates[1])
                    #for d in student.discipline_records:
                    #    d.date = d.date.strftime('%b %d, %Y')

        context['students'] = students
        return context

scaffold_reports.register('student_report', SisReport)
