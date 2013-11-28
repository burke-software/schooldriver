#   Copyright 2012 Burke Software and Consulting LLC
#   Author David M Burke <david@burkesoftware.com>
#   
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 3 of the License, or
#   (at your option) any later version.
#     
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#      
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#   MA 02110-1301, USA.

from django.shortcuts import render_to_response, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, Sum, Count, get_model
from django.forms.models import BaseModelFormSet, modelformset_factory
from django.forms.formsets import formset_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext

from models import StudentAttendance, CourseAttendance, AttendanceStatus, AttendanceLog
from forms import CourseAttendanceForm, AttendanceReportForm, AttendanceDailyForm, AttendanceViewForm
from forms import StudentAttendanceForm, StudentMultpleAttendanceForm
from ecwsp.schedule.models import Course
from ecwsp.sis.models import Student, UserPreference, Faculty, SchoolYear
from ecwsp.sis.helper_functions import Struct
from ecwsp.sis.template_report import TemplateReport
from ecwsp.administration.models import Template

import datetime

@user_passes_test(lambda u: u.has_perm('attendance.take_studentattendance') or
                  u.has_perm('attendance.change_studentattendance'))
def teacher_attendance(request, course=None):
    """ Take attendance. show course selection if there is more than one course
    """
    today = datetime.date.today()
    if request.user.has_perm('attendance.change_studentattendance'):
        courses = Course.objects.filter(
            homeroom=True,
            marking_period__start_date__lte=today,
            marking_period__end_date__gte=today)
    elif Faculty.objects.filter(username=request.user.username).count() == 1:
        teacher = Faculty.objects.get(username=request.user.username)
        courses = Course.objects.filter(
            homeroom=True,
            teacher=teacher,
            marking_period__start_date__lte=today,
            marking_period__end_date__gte=today)
        sec_courses = Course.objects.filter(
            homeroom=True,
            secondary_teachers=teacher,
            marking_period__start_date__lte=today,
            marking_period__end_date__gte=today)
        courses = courses | sec_courses
    else:
        messages.info(
            request,
            'You do not exists as a Teacher. Tell an administrator to create a teacher with your username. " \
                "Ensure "teacher" is checked off.')
        return HttpResponseRedirect(reverse('admin:index'))
    
    if course:
        course = Course.objects.get(id=course)
    else:
        if courses.count() > 1:
            return render_to_response(
                'attendance/teacher_attendance_which.html',
                {
                    'request': request,
                    'type':type,
                    'courses': courses}, RequestContext(request, {}))
        elif courses.count() == 0:
            messages.info(
                request,
                'You are a teacher, but have no courses with attendance. This may also occur if " \
                    "the course is not set to the current marking period.')
            return HttpResponseRedirect(reverse('admin:index'))
        course = courses[0]
    students = course.get_attendance_students()
    
    readonly = False
    msg = ""
    if AttendanceLog.objects.filter(date=datetime.date.today(), user=request.user, course=course).count() > 0:
        readonly = True
    AttendanceFormset = modelformset_factory(
        StudentAttendance, form=StudentAttendanceForm,
        extra=students.exclude(student_attn__date=datetime.date.today()).count())
    
    if request.method == 'POST':
        formset = AttendanceFormset(request.POST)
        if formset.is_valid():
            for form in formset.forms:
                object = form.save()
                LogEntry.objects.log_action(
                    user_id         = request.user.pk, 
                    content_type_id = ContentType.objects.get_for_model(object).pk,
                    object_id       = object.pk,
                    object_repr     = unicode(object), 
                    action_flag     = ADDITION
                )
            AttendanceLog(user=request.user, date=datetime.date.today(), course=course).save()
            messages.success(request, 'Attendance recorded')
            return HttpResponseRedirect(reverse('admin:index'))
        else:
            msg = "\nDuplicate entry detected! It's possible someone else is entering " \
                "attendance for these students at the same time. Please confirm attendance." \
                " If problems persist contact an administrator."
    
    initial = []
    enroll_notes = []
    for student in students:
        attendances = StudentAttendance.objects.filter(date=datetime.date.today(), student=student)
        if attendances.count():
            student.marked = True
            student.status = attendances[0].status
            student.notes = attendances[0].notes
        else:
            student.marked = False
            initial.append({'student': student.id, 'status': None, 'notes': None, 'date': datetime.date.today() })
            note = student.courseenrollment_set.filter(course=course)[0].attendance_note
            if note: enroll_notes.append(unicode(note))
            else: enroll_notes.append("")
    formset = AttendanceFormset(initial=initial, queryset=StudentAttendance.objects.none())
    
    # add notes to each form
    i = 0
    form_students = students.exclude(student_attn__date=datetime.date.today())
    for form in formset.forms:
        form.enroll_note = enroll_notes[i]
        form.student_display = form_students[i]
        i += 1
    
    # add form to each student, so we can use for student in students in the template
    i = 0
    forms = formset.forms
    for student in students:
        if not student.marked:
            student.form = forms[i]
            i += 1
    
    return render_to_response(
        'attendance/teacher_attendance.html',
        {
            'request': request,
            'readonly': readonly,
            'msg': msg,
            'formset': formset,
            'students': students,}, RequestContext(request, {}))

@permission_required('attendance.change_studentattendance')
def teacher_submissions(request):
	#imports required: AttendanceLog, Course, Faculty  - Jeff
    logs = AttendanceLog.objects.filter(date=datetime.date.today())
    homerooms = Course.objects.filter(homeroom=True)
    homerooms = homerooms.filter(marking_period__school_year__active_year=True)
    homerooms = homerooms.filter(coursemeet__day__contains=datetime.date.today().isoweekday()).distinct()
    submissions = []
    for homeroom in homerooms:
        submission = {}
        submission['homeroom'] = homeroom
        if homeroom.teacher:
            submission['teacher'] = homeroom.teacher
        log = AttendanceLog.objects.filter(date=datetime.date.today(), course=homeroom)
        if log.count() > 0:
            submission['submitted'] = "Yes"
            if log[0].user and Faculty.objects.filter(username=log[0].user.username):
                submission['submitted_by'] = Faculty.objects.filter(username=log[0].user.username)[0]
        else:
            submission['submitted'] = "No"
        submissions.append(submission)
    return render_to_response(
        'attendance/teacher_submissions.html',
        {'request': request, 'submissions': submissions})


def daily_attendance_report(adate, private_notes=False, type="odt", request=None):
    from ecwsp.sis.models import GradeLevel
    from ecwsp.sis.report import get_school_day_number
    template = Template.objects.get_or_create(name="Daily Attendance")[0]
    template = template.get_template_path(request)
    if not template:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))
    
    if request:
        report = TemplateReport(request.user)
    else:
        report = TemplateReport()
    report.data['selected_date'] = unicode(adate)
    report.data['school_day'] = get_school_day_number(adate)
    
    attendance = StudentAttendance.objects.filter(date=adate)
    students = Student.objects.filter(student_attn__in=attendance)
    
    active_year = SchoolYear.objects.get(active_year=True)
    active_year_dates = (active_year.start_date, active_year.end_date)
    
    for year in GradeLevel.objects.all():
        attns = attendance.filter(student__year__id=year.id)
        for attn in attns:
            if attn.status.absent:
                attn.total = StudentAttendance.objects.filter(student=attn.student, status__absent=True, status__half=False, date__range=active_year_dates).count()
                halfs = StudentAttendance.objects.filter(student=attn.student, status__absent=True, status__half=True,date__range=active_year_dates).count() / 2 
                attn.total += (float(halfs)/2)
            elif attn.status.tardy:
                attn.total = StudentAttendance.objects.filter(student=attn.student, status__tardy=True, date__range=active_year_dates).count()
            else:
                attn.total = StudentAttendance.objects.filter(student=attn.student, status=attn.status, date__range=active_year_dates).count()
        report.data['absences_' + str(year.id)] = attns
        
        attn_list = ""
        for status in AttendanceStatus.objects.exclude(name="Present"):
            attn = StudentAttendance.objects.filter(status=status, date=adate, student__year__id=year.id)
            if attn.count() > 0:
                attn_list += unicode(status.name) + " " + unicode(attn.count()) + ",  " 
        if len(attn_list) > 3: attn_list = attn_list[:-3]
        report.data['stat_' + str(year.id)] = attn_list
        
    
    report.data['comments'] = ""
    for attn in StudentAttendance.objects.filter(date=adate):
        if (attn.notes) or (attn.private_notes and private_notes):
            report.data['comments'] += unicode(attn.student) + ": "
            if attn.notes: report.data['comments'] += unicode(attn.notes) + "  "
            if attn.private_notes and private_notes: 
                report.data['comments'] += unicode(attn.private_notes) 
            report.data['comments'] += ",  "
    if len(report.data['comments']) > 3: report.data['comments'] = report.data['comments'][:-3]
    
    report.filename = "daily_attendance"
    return report.pod_save(template)

def check_attendance_permission(course, user):
    """ Returns true if user has permission to take attendance
    """
    if Faculty.objects.filter(username=user.username):
        teacher = Faculty.objects.get(username=user.username)
        if teacher == course.teacher or teacher in course.secondary_teachers.all():
            return True
    if user.has_perm('attendance.change_studentattendance'):
        return True
    raise PermissionDenied('User attempting to take attendance is unauthorized')
    
    
@permission_required('attendance.take_studentattendance')
def select_course_for_attendance(request):
    """ View for a teacher to select which course to take attendance for
    """
    today=datetime.datetime.now()
    if not Faculty.objects.filter(username=request.user.username):
        messages.info(
            request,
            'You do not exists as a Teacher. Tell an administrator to create a teacher with your username.')
        return HttpResponseRedirect(reverse('admin:index'))
    
    teacher = Faculty.objects.get(username=request.user.username)
    courses = Course.objects.filter(
        teacher=teacher,
        marking_period__start_date__lte=today,
        marking_period__end_date__gte=today)
    sec_courses = Course.objects.filter(
        secondary_teachers=teacher,
        marking_period__start_date__lte=today,
        marking_period__end_date__gte=today)
    courses = courses | sec_courses
    
    predicted_course = None
    if courses.filter(
        coursemeet__day__exact=today.isoweekday(),
        coursemeet__period__start_time__gt=today.time()
        ):
        predicted_course = courses.filter(
            coursemeet__day__exact=today.isoweekday(),
            coursemeet__period__start_time__gt=today.time(),
            ).order_by('coursemeet__period__start_time')[0]
    return render_to_response(
        'attendance/select_course_attendance.html',
        {
            'courses': courses,
            'predicted_course': predicted_course,
        },
        RequestContext(request, {}))
    

@permission_required('attendance.take_studentattendance')
def course_attendance(request, course_id, for_date=datetime.date.today):
    """ View for a teacher to take course attendance
    """
    for_date=datetime.date.today()
    course = get_object_or_404(Course, pk=course_id)
    check_attendance_permission(course, request.user)
    
    students = course.get_enrolled_students()
    daily_attendance = StudentAttendance.objects.filter(student__in=students,date=for_date).distinct()
    CourseAttendanceFormSet = formset_factory(CourseAttendanceForm, extra=0)
    
    if request.POST:
        formset = CourseAttendanceFormSet(request.POST)
        if formset.is_valid():
            number_created = 0
            for form in formset.forms:
                data = form.cleaned_data
                if data['status']:
                    number_created += 1
                    try:
                        course_attendance = CourseAttendance.objects.get(
                            student=data['student'],
                            course=course,
                            date=for_date,
                        )
                        course_attendance.status = data['status']
                        course_attendance.notes = data['notes']
                        course_attendance.time_in = data['time_in']
                        course_attendance.save()
                    except CourseAttendance.DoesNotExist:
                        CourseAttendance.objects.create(
                            student=data['student'],
                            course=course,
                            date=for_date,
                            status = data['status'],
                            notes = data['notes'],
                            time_in = data['time_in'],
                        )
            if number_created:
                messages.success(request, 'Attendance recorded for %s students' % number_created)
    else:
        initial_data = []
        for student in students:
            initial_row = {'student': student}
            if student.courseattendance_set.filter(date=for_date, course=course):
                current_attendance = student.courseattendance_set.filter(date=for_date)[0]
                initial_row['status'] = current_attendance.status
                initial_row['time_in'] = current_attendance.time_in
                initial_row['notes'] = current_attendance.notes
            elif student.student_attn.filter(date=for_date, status__absent=True):
                initial_row['status'] = AttendanceStatus.objects.get(name="Absent")
            initial_data.append(initial_row)
        formset = CourseAttendanceFormSet(initial=initial_data)
    
    i = 0
    for student in students:
        formset[i].student_name = student
        formset[i].student_attendance = ""
        formset[i].student_attendance_note = ""
        if student.student_attn.filter(date=for_date):
            for attendance in student.student_attn.filter(date=for_date):
                formset[i].student_attendance += unicode(attendance.status)
                formset[i].student_attendance_note += unicode(attendance.notes)
        i += 1
    
    return render_to_response(
        'attendance/course_attendance.html',
        {
            'course': course,
            'formset': formset,
            'for_date': for_date,
        },
        RequestContext(request, {}))


@permission_required('sis.reports') 
def attendance_report(request):
    from ecwsp.sis.xl_report import XlReport

    form = AttendanceReportForm()
    daily_form = AttendanceDailyForm()
    lookup_form = AttendanceViewForm()
    if request.method == 'POST':
        if "daily" in request.POST:
            daily_form = AttendanceDailyForm(request.POST)
            if daily_form.is_valid():
                type = UserPreference.objects.get_or_create(user=request.user)[0].get_format(type="document")
                return daily_attendance_report(
                    daily_form.cleaned_data['date'],
                    daily_form.cleaned_data['include_private_notes'],
                    type=type,
                    request=request,
                    )
        elif 'studentlookup' in request.POST:
            lookup_form = AttendanceViewForm(request.POST)
            if lookup_form.is_valid():
                type = UserPreference.objects.get_or_create(user=request.user)[0].get_format(type="document")
                return attendance_student(
                    request,
                    lookup_form.cleaned_data['student'].id,
                    all_years=lookup_form.cleaned_data['all_years'],
                    order_by=lookup_form.cleaned_data['order_by'],
                    include_private_notes=lookup_form.cleaned_data['include_private_notes'])
            else:
                return render_to_response(
                    'attendance/attendance_report.html',
                    {'request': request, 'form':form, 'daily_form': daily_form, 'lookup_form': lookup_form}); 
        else: 
            form = AttendanceReportForm(request.POST)
            if form.is_valid():
                attendances = StudentAttendance.objects.all()
                data = []
                titles = []
                attendances = attendances.filter(date__range=(form.get_dates()))
                if 'student' in request.POST: # by student
                    students = Student.objects.all()
                    if not form.cleaned_data['include_deleted']:
                        students = students.filter(is_active=True)
                    students = students.filter()
                    
                    titles.append("Student")
                    titles.append("Total Absences (not half)")
                    titles.append("Total Tardies")
                    for status in AttendanceStatus.objects.exclude(name="Present"):
                        titles.append(status)
                    pref = UserPreference.objects.get_or_create(user=request.user)[0]
                    students_absent = students.filter(
                        student_attn__status__absent=True,
                        student_attn__status__half=False,
                        student_attn__in=attendances).annotate(abs=Count('student_attn'))
                    students_tardy = students.filter(
                        student_attn__status__tardy=True,
                        student_attn__in=attendances).annotate(abs=Count('student_attn'))
                    attn_tardy = attendances.filter(status__tardy=True)
                    
                    students_each_total = {}
                    for status in AttendanceStatus.objects.exclude(name="Present"):
                        students_each_total[status.name] = students.filter(
                            student_attn__status=status,
                            student_attn__in=attendances).annotate(abs=Count('student_attn'))
                    
                    for student in students:
                        add = True
                        row = []
                        row.append(student)
                        if student in students_absent:
                            total_absent = students_absent.filter(id=student.id)[0].abs
                        else:
                            total_absent = 0
                        
                        if student in students_tardy:
                            total_tardy = students_tardy.filter(id=student.id)[0].abs
                        else:
                            total_tardy = 0
                            
                        if (total_absent >= form.cleaned_data['filter_total_absences'] and
                            total_tardy >= form.cleaned_data['filter_total_tardies']):
                            row.append( total_absent )
                            row.append( total_tardy )
                            for status in AttendanceStatus.objects.exclude(name="Present"):
                                count = 0
                                if student in students_each_total[status.name]:
                                    count = students_each_total[status.name].filter(id=student.id)[0].abs
                                row.append(count)
                                if (form.cleaned_data['filter_status'] == status and
                                    attendances.filter(
                                        student=student,
                                        status=status).count() < form.cleaned_data['filter_count']):
                                    add = False
                            if add: data.append(row)
                    report = XlReport(file_name="attendance_report")
                    report.add_sheet(data, header_row=titles, title="Attendance Report", heading="Attendance Report")
                    
                elif 'perfect_attendance' in request.POST:
                    form = AttendanceReportForm(request.POST)
                    if form.is_valid():
                        data = form.cleaned_data
                        template = Template.objects.get_or_create(name="Perfect attendance")[0]
                        template = template.get_template_path(request)
                        if not template:
                            return render_to_response(
                                'attendance/attendance_report.html',
                                {
                                    'form':form,
                                    'daily_form': daily_form,
                                    'lookup_form': lookup_form}, RequestContext(request, {}),)
                        
                        students = Student.objects.all()
                        perfect_students = []
                        if not form.cleaned_data['include_deleted']:
                            students = students.filter(is_active=True)
                        for student in students:
                            total_absent = attendances.filter(status__absent=True, student=student).count()
                            total_tardy = attendances.filter(status__tardy=True, student=student).count()
                            if not total_absent and not total_tardy:
                                perfect_students.append(student)
                        
                        format = UserPreference.objects.get_or_create(user=request.user)[0].get_format(type="document")
                        return pod_report_all(template, students=perfect_students, format=format)
                        
                else: # Aggregate report
                    stats = []
                    for status in AttendanceStatus.objects.exclude(name="Present"):
                        titles.append(status)
                        number = attendances.filter(status=status).count()
                        stats.append(number)
                    data.append(stats)
                    data.append([])
                    
                    students = Student.objects.filter(is_active=True).count()
                    absents = attendances.filter(status__absent=True).count()
                    if form.cleaned_data['marking_period']:
                        days = 0
                        for mp in form.cleaned_data['marking_period']:
                            days += mp.get_number_days()
                    else:
                        days = SchoolYear.objects.get(active_year=True).get_number_days()
                    #percentage = 1.0 - float(absents) / (float(students) * float(days))
                    percentage = '=1-(B4/(A4*C4))'
                    data.append(['Students', 'Total Absents', 'School days', 'Absent Percentage'])
                    data.append([students, absents, days, percentage])
                    
                    report = XlReport(file_name="attendance_report")
                    report.add_sheet(data, header_row=titles, title="Attendance Report")
                return report.as_download()
    return render_to_response(
        'attendance/attendance_report.html',
        {'form':form, 'daily_form': daily_form, 'lookup_form': lookup_form}, RequestContext(request, {}),)
    

def add_multiple(request):
    """ Add multple records by allowing multiple students in the form.
    Each student will make one new record
    """
    if request.POST:
        form = StudentMultpleAttendanceForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            created_records = 0
            updated_records = 0
            for student in data["student"]:
                record, created = StudentAttendance.objects.get_or_create(
                    student_id=student,
                    date=data['date'],
                    status=data['status'],
                )
                record.time=data['time']
                record.notes=data['notes']
                record.private_notes=data['private_notes']
                record.save()
                if created:
                    created_records += 1
                else:
                    updated_records += 1
            messages.success(
                request,
                'Created {0} and updated {1} attendance records'.format(created_records, updated_records),)
            
    else:
        form = StudentMultpleAttendanceForm()
    breadcrumbs = [
        {'link': reverse('admin:app_list', args=['attendance',]), 'name': 'Attendance'},
        {'link': reverse('admin:attendance_studentattendance_changelist'), 'name': 'Student attendances'},
        {'name': 'Take multiple'},
    ]
    return render_to_response(
        'sis/generic_form.html',
        {'form':form, 'breadcrumbs': breadcrumbs}, RequestContext(request, {}),)

    
def attendance_student(request, id, all_years=False, order_by="Date", include_private_notes=False):
    """ Attendance report on particular student """
    from ecwsp.sis.template_report import TemplateReport
    report = TemplateReport(request.user)
    student = Student.objects.get(id=id)
    if all_years:
        attendances = StudentAttendance.objects.filter(student=student)
    else:
        active_year = SchoolYear.objects.get(active_year=True)
        active_year_dates = (active_year.start_date, active_year.end_date)
        attendances = StudentAttendance.objects.filter(student=student, date__range=active_year_dates)
    if order_by == "Status": attendances = attendances.order_by('status') 
    
    report.data['attendances'] = []
    
    for attn in attendances:
        if include_private_notes:
            notes = unicode(attn.notes) + "  " + unicode(attn.private_notes)
        else:
            notes = unicode(attn.notes)
        attendance = Struct()
        attendance.date = attn.date
        attendance.status = attn.status
        attendance.notes = notes
        report.data['attendances'].append(attendance)
              
   # data['attendances'] = attendances
    report.data['student'] = student
    report.data['student_year'] = student.year
    
    template = Template.objects.get_or_create(name="Student Attendance Report")[0]
    template = template.get_template_path(request)
    report.filename = unicode(student) + "_Attendance"
    return report.pod_save(template)
