from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper

from ecwsp.sis.models import *
from ecwsp.sis.uno_report import uno_save
from ecwsp.administration.models import *
from ecwsp.schedule.models import *
from ecwsp.schedule.calendar import *

from ecwsp.appy.pod.renderer import Renderer
import tempfile
import os
import uno
from decimal import *

class struct(object):
    def __unicode__(self):
        return ""

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


def pod_save(filename, ext, data, template, get_tmp_file=False):
    import time
    file_name = tempfile.gettempdir() + '/appy' + str(time.time()) + ext
    renderer = Renderer(template, data, file_name)
    renderer.run()
    
    if ext == ".doc":
        content = "application/msword"
    elif ext == ".docx":
        content = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif ext == ".pdf":
        content = "application/pdf"
    elif ext == ".rtf":
        content = "application/rtf"
    else: # odt, prefered
        content = "application/vnd.oasis.opendocument.text"
        
    if get_tmp_file:
        return file_name
    
    wrapper = FileWrapper(file(file_name)) # notice not using the tmp file! Not ideal.
    response = HttpResponse(wrapper, content_type=content)
    response['Content-Length'] = os.path.getsize(file_name)
    response['Content-Disposition'] = 'attachment; filename=' + filename + ext
    try: os.remove(file_name)
    except: pass # this sucks. But Ubuntu can't run ooo as www-data
    
    return response


def get_default_data():
    data={}
    school_name, created = Configuration.objects.get_or_create(name="School Name")
    data['school_name'] = unicode(school_name.value)
    data['school_year'] = unicode(SchoolYear.objects.get(active_year=True))
    data['date'] = unicode(date.today().strftime('%b %d, %Y'))
    data['long_date'] = unicode(date.today().strftime('%B %d, %Y'))
    return data


def daily_attendance_report(date, private_notes=False, type="odt"):
    template = Template.objects.get_or_create(name="Daily Attendance")[0]
    template = template.file.path
    
    data = get_default_data()
    data['selected_date'] = unicode(date)
    data['school_day'] = get_school_day_number(date)
    
    attendance = StudentAttendance.objects.filter(date=date)
    students = Student.objects.filter(student_attn__in=attendance)
    
    active_year = SchoolYear.objects.get(active_year=True)
    active_year_dates = (active_year.start_date, active_year.end_date)
    
    for year in GradeLevel.objects.all():
        attns = attendance.filter(student__year__id=year.id)
        for attn in attns:
            if attn.status.absent:
                attn.total = StudentAttendance.objects.filter(student=attn.student, status__absent=True, date__range=active_year_dates).count()
            elif attn.status.tardy:
                attn.total = StudentAttendance.objects.filter(student=attn.student, status__tardy=True, date__range=active_year_dates).count()
            else:
                attn.total = StudentAttendance.objects.filter(student=attn.student, status=attn.status, date__range=active_year_dates).count()
        data['absences_' + str(year.id)] = attns
        
        attn_list = ""
        for status in AttendanceStatus.objects.exclude(name="Present"):
            attn = StudentAttendance.objects.filter(status=status, date=date, student__year__id=year.id)
            if attn.count() > 0:
                attn_list += unicode(status.name) + " " + unicode(attn.count()) + ",  " 
        if len(attn_list) > 3: attn_list = attn_list[:-3]
        data['stat_' + str(year.id)] = attn_list
        
    
    data['comments'] = ""
    for attn in StudentAttendance.objects.filter(date=date):
        if (attn.notes) or (attn.private_notes and private_notes):
            data['comments'] += unicode(attn.student) + ": "
            if attn.notes: data['comments'] += unicode(attn.notes) + "  "
            if attn.private_notes and private_notes: 
                data['comments'] += unicode(attn.private_notes) 
            data['comments'] += ",  "
    if len(data['comments']) > 3: data['comments'] = data['comments'][:-3]
    
    filename = "daily_attendance"
    return pod_save(filename, "." + str(type), data, template)


def attendance_student(id, all_years=False, order_by="Date", include_private_notes=False, type="odt"):
    """ Attendance report on particular student """
    student = Student.objects.get(id=id)
    if all_years:
        attendances = StudentAttendance.objects.filter(student=student)
    else:
        active_year = SchoolYear.objects.get(active_year=True)
        active_year_dates = (active_year.start_date, active_year.end_date)
        attendances = StudentAttendance.objects.filter(student=student, date__range=active_year_dates)
    if order_by == "Status": attendances = attendances.order_by('status') 
    
    data = get_default_data()
    
    data['attendances'] = []
    
    for attn in attendances:
        if include_private_notes:
            notes = unicode(attn.notes) + "  " + unicode(attn.private_notes)
        else:
            notes = unicode(attn.notes)
        attendance = struct()
        attendance.date = attn.date
        attendance.status = attn.status
        attendance.notes = notes
        data['attendances'].append(attendance)
              
   # data['attendances'] = attendances
    data['student'] = student
    data['student_year'] = student.year
    
    template = Template.objects.get_or_create(name="Student Attendance Report")[0]
    filename = unicode(student) + "_Attendance"
    return pod_save(filename, "." + str(type), data, template.file.path)

def pod_report(template, data, filename, format="odt"):
    data = dict(data.items() + get_default_data().items())
    return pod_save(filename, "." + str(format), data, template)

def pod_report_all(template, options=None, students=None, format="odt"):
    """ options is from StudentReportWriterForm, it includes the time range
    and some other options """
    data = get_default_data()
    try:
        if options['student'].count == 1:
            data['student'] = options['student'][0]
    except: pass
    
    cal = Calendar()
    current_mp = MarkingPeriod.objects.filter(end_date__gte=date.today()).order_by('-start_date')
    if current_mp:
        for student in students:
            student.schedule_days, student.periods = cal.build_schedule(student, current_mp[0])
    
    data['students'] = students
    filename = 'output'
    return pod_save(filename, "." + str(format), data, template)

def pod_report_paper_attendance(day, format="odt"):
    """ Print paper attendance. Monday = 1, etc """
    template = Template.objects.get_or_create(name="Paper Attendance")[0].file
    cm = CourseMeet.objects.filter(day=day)
    courses = Course.objects.filter(coursemeet__in=cm, homeroom=True).distinct()
    data = get_default_data()
    data['courses'] = courses
    return pod_save("Paper Attendance", "." + str(format), data, template)

def pod_report_work_study(template, students, format="odt"):
    """ options is from StudentReportWriterForm, it includes the time range
    and some other options """
    from ecwsp.work_study.models import WorkTeam
    data = get_default_data()
    data['workteams'] = WorkTeam.objects.all()
    data['students'] = students
    
    filename = 'Work Study Report'
    return pod_save(filename, "." + str(format), data, template)  
    
def pod_report_grade(template, options, students, format="odt", transcript=True, report_card=True):
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
     
    data = get_default_data()
    
    blank_grade = struct()
    blank_grade.comment = ""
    
    #if options['marking_period']:
    #    marking_periods = options['marking_period']
    #elif options['this_year']:
    #    marking_periods = MarkingPeriod.objects.filter(school_year=SchoolYear.objects.get(active_year=True))
    #else:
    for_date = options['date'] # In case we want a transcript from a future date
    
    # if benchmark grading is installed and enabled for the current school year,
    # and this is a report card, bail out to another function
    if (report_card and
        "ecwsp.benchmark_grade" in settings.INSTALLED_APPS and
        SchoolYear.objects.filter(start_date__lt=for_date).order_by('-start_date')[0].benchmark_grade):
        from ecwsp.benchmark_grade.report import benchmark_report_card
        return benchmark_report_card(template, options, students, format)
        
    if (transcript and "ecwsp.benchmark_grade" in settings.INSTALLED_APPS):
        from ecwsp.benchmark_grade.models import Aggregate, Category
        
    marking_periods = MarkingPeriod.objects.filter(
        school_year=SchoolYear.objects.filter(
            start_date__lt=for_date, end_date__lt=for_date
        ).order_by(
            '-start_date'
        )[0]
    ).filter(show_reports=True)
    data['marking_periods'] = marking_periods.order_by('start_date')
    
    for student in students:
        # for report_card
        if report_card:
            courses = Course.objects.filter(
                courseenrollment__user=student,
                graded=True,
            )
            
            courses = courses.filter(marking_period__in=marking_periods).distinct().order_by('department')
            for course in courses:
                i = 1
                for grade in course.grade_set.filter(student=student, final=True):
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
            student.tardy_total = 0
            student.dismissed_total = 0
            for mp in marking_periods.order_by('start_date'):
                absent = student.student_attn.filter(status__absent=True, date__range=(mp.start_date, mp.end_date)).count()
                tardy = student.student_attn.filter(status__tardy=True, date__range=(mp.start_date, mp.end_date)).count()
                dismissed = student.student_attn.filter(status__code="D", date__range=(mp.start_date, mp.end_date)).count()
                student.absent_total += absent
                student.tardy_total += tardy
                student.dismissed_total += dismissed
                setattr(student, "absent" + str(i), absent)
                setattr(student, "tardy" + str(i), tardy)
                setattr(student, "dismissed" + str(i), dismissed)
                i += 1
            while i <= 6:
                setattr(student, "absent" + str(i), "")
                setattr(student, "tardy" + str(i), "")
                setattr(student, "dismissed" + str(i), "")
                i += 1
        
        ## for transcripts
        if transcript:
            student.years = SchoolYear.objects.filter(markingperiod__course__courseenrollment__user=student, end_date__lte=for_date).exclude(omityeargpa__student=student).distinct().order_by('start_date')
            for year in student.years:
                year.credits = 0
                year.mps = MarkingPeriod.objects.filter(course__courseenrollment__user=student, school_year=year, show_reports=True).distinct().order_by("start_date")
                i = 1
                for mp in year.mps:
                    setattr(year, "mp" + str(i), mp.shortname)
                    i += 1
                while i <= 6:
                    setattr(year, "mp" + str(i), "")
                    i += 1
                year.courses = Course.objects.filter(courseenrollment__user=student, graded=True, marking_period__school_year=year, marking_period__show_reports=True).distinct().order_by('department')
                year_grades = student.grade_set.filter(final=True, marking_period__show_reports=True, marking_period__end_date__lte=for_date)
                # course grades
                for course in year.courses:
                    # Grades
                    course_grades = year_grades.filter(course=course).distinct()
                    course_aggregates = None
                    if year.benchmark_grade:
                        course_aggregates = Aggregate.objects.filter(singleCourse=course, singleStudent=student)
                    i = 1
                    for mp in year.mps:
                        if year.benchmark_grade:
                            try:
                                standards = course_aggregates.get(singleCategory=Category.objects.get(name='Standards'), singleMarkingPeriod=mp)
                                standards = standards.scale.spruce(standards.cachedValue)
                            except:
                                standards = ""
                            try:
                                engagement = course_aggregates.get(singleCategory=Category.objects.get(name='Engagement'), singleMarkingPeriod=mp)
                                engagement = engagement.scale.spruce(engagement.cachedValue)
                            except:
                                engagement = ""
                            try:
                                organization = course_aggregates.get(singleCategory=Category.objects.get(name='Organization'), singleMarkingPeriod=mp)
                                organization = organization.scale.spruce(organization.cachedValue)
                            except:
                                organization = ""
                            setattr(course, "grade" + str(i), standards)
                            setattr(course, "engagement" + str(i), engagement)
                            setattr(course, "organization" + str(i), organization)
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
                        if year.benchmark_grade:
                            setattr(course, "engagement" + str(i), "")
                            setattr(course, "organization" + str(i), "")
                        i += 1
                    course.final = course.get_final_grade(student, date_report=for_date)
                    
                    if mp.end_date < for_date and course.is_passing(student) and course.credits:
                        year.credits += course.credits
                
                # Averages per marking period
                i = 1
                for mp in year.mps:
                    if mp.end_date < for_date:
                        setattr(year, 'mp' + str(i) + 'ave', student.calculate_gpa_mp(mp))
                        i += 1
                while i <= 6:
                    setattr(year, 'mp' + str(i) + 'ave', "")
                    i += 1
                
                year.ave = student.calculate_gpa_year(year)
                
                # Attendance for year
                year.total_days = year.get_number_days()
                year.nonmemb = student.student_attn.filter(status__code="nonmemb", date__range=(year.start_date, year.end_date)).count()
                year.absent = student.student_attn.filter(status__absent=True, date__range=(year.start_date, year.end_date)).count()
                year.tardy = student.student_attn.filter(status__tardy=True, date__range=(year.start_date, year.end_date)).count()
                year.dismissed = student.student_attn.filter(status__code="D", date__range=(year.start_date, year.end_date)).count() 
            
            # credits per dept    
            student.departments = Department.objects.filter(course__courseenrollment__user=student).distinct()
            student.departments_text = ""
            for dept in student.departments:
                c = 0
                for course in student.course_set.filter(department=dept, marking_period__school_year__end_date__lt=for_date, graded=True).distinct():
                    if course.credits and course.is_passing(student):
                        c += course.credits
                dept.credits = c
                student.departments_text += "| %s: %s " % (dept, dept.credits)
            student.departments_text += "|"
            
            student.tests = []
            student.highest_tests = []
            for test_result in student.standardtestresult_set.filter(test__show_on_reports=True).order_by('test'):
                test_result.categories = ""
                for cat in test_result.standardcategorygrade_set.filter(category__is_total=False):
                    test_result.categories += '%s: %s  |  ' % (cat.category.name, cat.grade)
                test_result.categories = test_result.categories [:-3]
                student.tests.append(test_result)
                
            for test in StandardTest.objects.filter(standardtestresult__student=student, show_on_reports=True).distinct():
                test.total = test.get_cherry_pick_total(student)
                student.highest_tests.append(test)

    try:
        if options['student'].count == 1:
            data['student'] = options['student'][0]
    except: pass
    
    data['students'] = students
    filename = 'output'
    return pod_save(filename, "." + str(format), data, template)
