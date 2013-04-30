from django.http import HttpResponse
from django.conf import settings
from django.core.servers.basehttp import FileWrapper

from ecwsp.sis.models import SchoolYear, Configuration, UserPreference
from ecwsp.sis.uno_report import uno_save
from ecwsp.administration.models import *
from ecwsp.schedule.models import *
from ecwsp.schedule.calendar import *
from ecwsp.sis.template_report import TemplateReport

from appy.pod.renderer import Renderer
from django.contrib.auth.decorators import user_passes_test
import tempfile
import os
from decimal import *
import datetime

class struct(object):
    def __unicode__(self):
        return ""

def strip_trailing_zeros(x):
    x = str(x).strip()
    # So sayeth Alex Martelli
    # http://stackoverflow.com/a/2440786
    return x.rstrip('0').rstrip('.')

def get_school_day_number(date):
    mps = MarkingPeriod.objects.filter(school_year__active_year=True).order_by('start_date')
    current_day = mps[0].start_date
    day = 0
    while current_day <= date:
        is_day = False
        for mp in mps:
            if current_day >= mp.start_date and current_day <= mp.end_date:
                days_off = []
                for d in mp.daysoff_set.all().values_list('date'): days_off.append(d[0])
                if not current_day in days_off:
                    if mp.monday and current_day.isoweekday() == 1:
                        is_day = True
                    elif mp.tuesday and current_day.isoweekday() == 2:
                        is_day = True
                    elif mp.wednesday and current_day.isoweekday() == 3:
                        is_day = True
                    elif mp.thursday and current_day.isoweekday() == 4:
                        is_day = True
                    elif mp.friday and current_day.isoweekday() == 5:
                        is_day = True
                    elif mp.saturday and current_day.isoweekday() == 6:
                        is_day = True
                    elif mp.sunday and current_day.isoweekday() == 7:
                        is_day = True
        if is_day: day += 1
        current_day += timedelta(days=1)
    return day


class GradeTemplateReport(TemplateReport):
    def __init__(self, user):
        self.user = user
        super(GradeTemplateReport, self).__init__(user)
        
    def get_student_report_card_data(self, student):
        courses = Course.objects.filter(
            courseenrollment__user=student,
            graded=True,
        )
        courses = courses.filter(marking_period__in=marking_periods).distinct().order_by('department')
        for course in courses:
            grades = course.grade_set.filter(student=student).filter(
                marking_period__isnull=False,
                marking_period__show_reports=True)
            i = 1
            for grade in grades:
                # course.grade1, course.grade2, etc
                setattr(course, "grade" + str(i), grade)
                i += 1
            while i <= 4:
                setattr(course, "grade" + str(i), blank_grade)
                i += 1
            course.final = course.get_final_grade(student)
        student.courses = courses
        
        #Attendance for marking period
        i = 1
        student.absent_total = 0
        student.absent_unexcused_total = 0
        student.tardy_total = 0
        student.tardy_unexcused_total = 0
        student.dismissed_total = 0
        for mp in marking_periods.order_by('start_date'):
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
        # benchmark_grade transcripts aren't radically different,
        # but they have some additional data
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
            year.courses = Course.objects.filter(courseenrollment__user=student, graded=True, marking_period__school_year=year, marking_period__show_reports=True).distinct()
            year.courses = UserPreference.objects.get_or_create(user=self.user)[0].sort_courses(year.courses)
            year_grades = student.grade_set.filter(marking_period__show_reports=True, marking_period__end_date__lte=self.for_date)
            # course grades
            for course in year.courses:
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
                            grade = "   " + str(grade) + "   "
                        except:
                            grade = ""
                        setattr(course, "grade" + str(i), grade)
                    i += 1
                while i <= 6:
                    setattr(course, "grade" + str(i), "")
                    i += 1
                course.final = course.get_final_grade(student, date_report=self.for_date)
                
                if (mp.end_date < self.for_date and
                    course.is_passing(
                        student,
                        cache_grade=course.final,
                        cache_passing=self.passing_grade,
                        cache_letter_passing=self.letter_passing_grade) and
                    course.credits):
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
                if mp.end_date < self.for_date:
                    setattr(year, 'mp' + str(i) + 'ave', student.calculate_gpa_mp(mp))
                    i += 1
            while i <= 6:
                setattr(year, 'mp' + str(i) + 'ave', "")
                i += 1
            
            year.ave = student.calculate_gpa_year(year, self.for_date)
            
            
            # Attendance for year
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
                    if course.credits and course.is_passing(
                        student,
                        cache_passing=self.passing_grade,
                        cache_letter_passing=self.letter_passing_grade):
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
                        test_result.categories += '%s: %s  |  ' % (cat.category.name, strip_trailing_zeros(cat.grade))
                    test_result.categories = test_result.categories [:-3]
                    student.tests.append(test_result)
                    
                for test in StandardTest.objects.filter(standardtestresult__student=student, show_on_reports=True, standardtestresult__show_on_reports=True).distinct():
                    test.total = strip_trailing_zeros(test.get_cherry_pick_total(student))
                    student.highest_tests.append(test)
                    
                    
    def pod_report_grade(self, template, options, students, transcript=True, report_card=True, benchmark_report_card=True):
        """ Generate report card and transcript grades via appy
        variables for apply:
        students                - contails all each student
        students.courses        - courses for the student (usually for report cards, one year)
        students.years          - years student is enrolled (and selected)
        students.years.courses  - courses for one year (usually for transcripts that span multiple years)
        year                    - Selected school year
        students.phone          - First phone number for student
        students.sat_highest    - Highest possible combination of SAT test scores. Looks for test named "SAT"
        students.years.ave      - Averaged grade for year
        students.years.total_days- School days this year
        students.years.absent   - Absents for year
        students.years.tardy    - Tardies for year
        students.years.dismissed - Dismissed for year
        studnets.years.credits  - Total credits for year
        """
        blank_grade = struct()
        blank_grade.comment = ""
        
        self.passing_grade = float(Configuration.get_or_default("Passing Grade", '70').value)
        self.letter_passing_grade = Configuration.get_or_default("Letter Passing Grade", 'A,B,C,P').value
        self.year_days = {} # cache dict of school days in a year
        self.for_date = options['date'] # In case we want a transcript from a future date
        today = datetime.date.today()
        self.data['date_of_report'] = self.for_date # In case we want to include a python date on our template, which is a bit gross
        try: omit_substitutions = options['omit_substitutions']
        except KeyError: omit_substitutions = False
        
        # if benchmark grading is installed and enabled for the selected template,
        # and this is a report card, bail out to another function
        if (benchmark_report_card and
            "ecwsp.benchmark_grade" in settings.INSTALLED_APPS):
            from ecwsp.benchmark_grade.report import benchmark_report_card
            return benchmark_report_card(self, template, options, students)
        
        self.marking_periods = MarkingPeriod.objects.filter(
            school_year=SchoolYear.objects.filter(
                start_date__lt=self.for_date
            ).order_by(
                '-start_date'
            )[0]
        ).filter(show_reports=True)
        self.data['marking_periods'] = self.marking_periods.order_by('start_date')
        
        for student in students:
            # Can only use cache gpa if the report date is today.
            if self.for_date == today:
                student.current_report_cumulative_gpa = student.cache_gpa
            else:
                student.current_report_cumulative_gpa = student.calculate_gpa(self.for_date)
    
            # for report_card
            if report_card:
                self.get_student_report_card_data(student)
            ## for transcripts
            if transcript:
                self.get_student_transcript_data(student, omit_substitutions)
                
        try:
            if options['student'].count == 1:
                self.data['student'] = options['student'][0]
        except: pass
        
        self.data['students'] = students
        self.data['strip_trailing_zeros'] = strip_trailing_zeros
        return self.pod_save(template)
