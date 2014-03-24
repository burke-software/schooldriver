from scaffold_report.report import ScaffoldReport, scaffold_reports, ReportButton
from scaffold_report.fields import SimpleCompareField
from scaffold_report.filters import Filter, DecimalCompareFilter, IntCompareFilter, ModelMultipleChoiceFilter, ModelChoiceFilter
from django import forms
from django.conf import settings
from django.db.models import Count
from ecwsp.administration.models import Template, Configuration
from ecwsp.sis.models import Student, SchoolYear, GradeLevel
from ecwsp.schedule.models import MarkingPeriod, Department
from ecwsp.discipline.models import DisciplineAction
import datetime
from decimal import Decimal

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


class TemplateSelection(ModelChoiceFilter):
    """ Select a template for an appy report
    May affect what extra context is needed (for report cards and transcripts)
    """
    model = Template
    default = True
    can_add = False
    can_delete = False
    
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


from ajax_select.fields import AutoCompleteSelectMultipleField, AutoCompleteSelectField
class SelectSpecificStudents(ModelMultipleChoiceFilter):
    model = Student
    compare_field_string = "pk"
    default = True
    can_add = False

    def build_form(self):
        queryset = self.get_queryset()
        self.form = forms.Form()
        self.form.fields['filter_number'] = forms.IntegerField(widget=forms.HiddenInput())
        self.form.fields['field_0'] =  AutoCompleteSelectMultipleField('dstudent', required=False)

    def queryset_filter(self, queryset, report_context=None, **kwargs):
        if self.cleaned_data['field_0']:
            return super(SelectSpecificStudents, self).queryset_filter(queryset, report_context, **kwargs)
        return queryset
    

class AspReportButton(ReportButton):
    name = "asp_report"
    name_verbose = "ASP Report"
    
    def get_report(self, context):
        pass


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
    filters = (
        DecimalCompareFilter(verbose_name="Filter by GPA", compare_field_string="cached_gpa", add_fields=('gpa',)),
        AbsenceFilter(),
        TardyFilter(verbose_name="Tardies"),
        DisciplineFilter(),
        SchoolDateFilter(),
        StudentYearFilter(),
        SelectSpecificStudents(),
        MpGradeFilter(),
        CourseGradeFilter(),
        TemplateSelection(),
        IncludeDeleted(),
    )
    report_buttons = (
        AspReportButton(),
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
            start_date__lt=self.for_date,
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
            year.courses = student.course_set.filter(graded=True, marking_period__school_year=year, marking_period__show_reports=True).distinct()
            year_grades = student.grade_set.filter(marking_period__show_reports=True, marking_period__end_date__lte=self.report_context['date_begin'])
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
                        except:
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
                    marking_period__school_year__end_date__lt=self.for_date,
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
            self.for_date = self.report_context['date_begin']
            if template.transcript:
                self.pass_score = float(Configuration.get_or_default("Passing Grade", '70').value)
                self.pass_letters = Configuration.get_or_default("Letter Passing Grade", 'A,B,C,P').value
                for student in students:
                    self.get_student_transcript_data(student)
            if template.report_card:
                self.blank_grade = struct()
                self.blank_grade.comment = ""
                school_year = SchoolYear.objects.filter(start_date__lt=self.for_date
                        ).order_by('-start_date').first()
                context['year'] = school_year
                self.marking_periods = MarkingPeriod.objects.filter(
                    school_year=school_year, show_reports=True)
                context['marking_periods'] = self.marking_periods.order_by('start_date')
                for student in students:
                    self.get_student_report_card_data(student)

        context['students'] = students
        return context

scaffold_reports.register('student_report', SisReport)
