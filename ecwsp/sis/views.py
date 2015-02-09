from django.shortcuts import render_to_response, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import (
    login_required, user_passes_test, permission_required)
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.db import transaction
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.safestring import mark_safe
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.generic.base import TemplateView
from datetime import date

from .models import Student, UserPreference, GradeLevel, SchoolYear
from .forms import UserPreferenceForm, StudentLookupForm
from .forms import YearSelectForm
from .pdf_reports import student_thumbnail
from .template_report import TemplateReport
from ecwsp.administration.models import Template
from ecwsp.schedule.calendar import Calendar
from ecwsp.schedule.models import (
    MarkingPeriod, CourseSection, CourseEnrollment)

import sys


@login_required
def user_preferences(request):
    """ Displays user preferences
    """
    profile = UserPreference.objects.get_or_create(user=request.user)[0]
    if request.POST:
        password_form = PasswordChangeForm(user=request.user, data=request.POST)
        form = UserPreferenceForm(request.POST, instance=profile)
        if "password_change" in request.POST and password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, password_form.user)
        elif form.is_valid():
                form.cleaned_data['user'] = request.user
                form.save()
                messages.info(request, 'Successfully updated preferences')
                if 'refer' in request.GET and request.GET['refer']:
                    return HttpResponseRedirect(request.GET['refer'])
                return HttpResponseRedirect(reverse('admin:index'))
    else:
        form = UserPreferenceForm(instance=profile)
        password_form = PasswordChangeForm(user=request.user)
    return render_to_response('sis/user_preferences.html', {
        'form': form,
        'password_form': password_form,
    }, RequestContext(request, {}),)


@login_required
def index(request):
    """if student, redirect them to timesheet.  if faculty allow this page
    """
    if 'next' in request.GET and request.GET['next'] != "/":
        return HttpResponseRedirect(request.GET['next'])
    if request.user.is_staff:
        return HttpResponseRedirect('/sis/dashboard')
    elif request.user.groups.filter(Q(name='students')).count() > 0:
        return student_redirect(request)
    elif request.user.groups.filter(name='family').count() > 0:
        return family_redirect(request)
    elif request.user.groups.filter(Q(name='company')).count() > 0:
        from ecwsp.work_study.views import supervisor_dash
        return supervisor_dash(request)
    else:
        return render_to_response(
            'base.html',
            {'msg': "Not authorized", 'request': request},
            RequestContext(request, {}))


def student_redirect(request):
    """ Redirects student to proper page based on what's installed and if it's
    possible to display the timesheet
    """
    if 'ecwsp.work_study' in settings.INSTALLED_APPS:
        from ecwsp.work_study.views import student_timesheet
        from ecwsp.work_study.models import StudentWorker
        try:
            student = StudentWorker.objects.get(username=request.user.username)
        except ObjectDoesNotExist:
            student = None
        if student and hasattr(student, 'placement') and student.placement:
            return student_timesheet(request)
    return render_to_response('base.html', {'msg': "Welcome!", 'student': 'student', 'request': request,}, RequestContext(request, {}))

def family_redirect(request):
    if 'ecwsp.benchmark_grade' in settings.INSTALLED_APPS:
        from ecwsp.benchmark_grade.views import student_report
        return student_report(request)
    return render_to_response('base.html', {'msg': "Welcome!", 'request': request,}, RequestContext(request, {}))

@user_passes_test(lambda u: u.has_perm("sis.view_student"))
def photo_flash_card(request, year=None):
    """ Simple flash card game"""
    students = Student.objects.filter(is_active=True)
    grade_levels = GradeLevel.objects.all()
    try:
        if request.POST:
            form = StudentLookupForm(request.POST, request.FILES)
            if form.is_valid():
                student_id = form.cleaned_data['student']
            else:
                student_id = students.order_by('?')[0].pk
        else:
            form = StudentLookupForm()
            if year:
                student_id = students.filter(year=GradeLevel.objects.get(id=year)).order_by('?')[0].pk
            else:
                student_id = students.order_by('?')[0].pk
        student = Student.objects.filter(is_active=True).get(pk=student_id)
    except:
        messages.error(request, 'Student not found')
        return HttpResponseRedirect(reverse('admin:index'))
    return render_to_response('sis/flashcard.html',
                              {'form': form,
                               'student_name': student,
                               'grade_levels':grade_levels,
                               'student_img': student.pic.url_530x400,
                               'request': request}, RequestContext(request, {}))

def thumbnail(request, year):
    return student_thumbnail(request, GradeLevel.objects.get(id=year))

def paper_attendance(request, day):
    format = UserPreference.objects.get_or_create(user=request.user)[0].get_format(type="document")
    template = Template.objects.get_or_create(name="Paper Attendance")[0].file
    if not template:
        result = False
    else:
        from ecwsp.schedule.models import CourseMeet
        cm = CourseMeet.objects.filter(day=day)
        course_sections = CourseSection.objects.filter(coursemeet__in=cm, course__homeroom=True).distinct()
        report = TemplateReport(request.user)
        report.data['course_sections'] = course_sections
        result = report.pod_save(template)
    if result:
        return result
    else:
        messages.error(request, 'Problem making paper attendance, does the template exist?')
        return HttpResponseRedirect('/')

from scaffold_report.views import DownloadReportView, ScaffoldReportView
from .scaffold_reports import SisReport, AttendanceReport


class AttendanceReportView(ScaffoldReportView):
    template_name = 'sis/scaffold/CourseAttendance.html'

    def get_context_data(self, **kwargs):
        context = super(AttendanceReportView, self).get_context_data(**kwargs)
        context['report'] = AttendanceReport
        context['filters'] = AttendanceReport.filters
        return context

@user_passes_test(lambda u: u.has_perm("sis.view_student"))
def transcript_nonofficial(request, student_id):
    """ Build a transcripte based on template called "Transcript Nonoffical"
    """
    students = Student.objects.filter(pk=student_id)
    template = Template.objects.filter(name="Transcript Nonoffical").first()
    if not template:
        messages.error(request, 'This feature requires a "Transcript Nonoffical" template.')
        return HttpResponseRedirect('/')
    school_year = SchoolYear.objects.get(active_year=True)
    today = date.today()

    view = DownloadReportView()
    view.report = SisReport()
    view.report.student_queryset = students
    view.report.report_context = {
        'template': template,
        'date_begin': today,
        'date_end': today.replace(today.year + 50),
        'school_year': school_year,
    }
    get = request.GET.copy()
    get['type'] = 'appy'
    request.GET = get
    return view.post(request)


def logout_view(request):
    """ Logout, by sending a message to the base.html template
    """
    logout(request)
    msg = mark_safe('You have been logged out. Click <a href="/">here</a> to log back in.')
    return render_to_response('base.html', {'msg': msg,}, RequestContext(request, {}))

@permission_required('sis.change_student')
def import_naviance(request):
    """ Import only naviance data
    """
    from ecwsp.standard_test.forms import UploadNaviance
    msg = 'Import a test directly from Naviance such as SAT and ACT. You must have unique id (SWORD) and hs_student_id (Naviance)' \
          ' be the same. You must have already set up the <a href="/admin/schedule/standardtest/"> tests </a> <br/>' \
          'In Naviance, click setup, then Import/Export then export the test you want. At this time only SAT and ACT is supported.'
    if request.method == 'POST':
        form = UploadNaviance(request.POST, request.FILES)
        if form.is_valid():
            test = form.cleaned_data['test']
            from ecwsp.sis.importer import Importer
            importer = Importer(file=form.cleaned_data['import_file'], user=request.user)
            msg, filename = importer.import_just_standard_test(test)
            msg += '<br/><a href="/media/import_error.xls">Download Errors</a>'
    else:
        form = UploadNaviance()
    msg = mark_safe(msg)
    return render_to_response('sis/generic_form.html', {'form':form, 'msg':msg}, RequestContext(request, {}), )

@login_required
def ajax_include_deleted(request):
    """ ajax call to enable or disable user preference to search for inactive students
    """
    checked = request.GET.get('checked')
    profile = UserPreference.objects.get_or_create(user=request.user)[0]
    if checked == "true":
        profile.include_deleted_students = True
    else:
        profile.include_deleted_students = False
    profile.save()
    return HttpResponse('SUCCESS')

@user_passes_test(lambda u: u.has_perm("sis.view_student"))
def view_student(request, id=None):
    """ Lookup all student information
    """
    if request.method == "GET":
        if id and 'next' in request.GET or 'previous' in request.GET:
            current_student = get_object_or_404(Student, pk=id)
            found = False
            preference = UserPreference.objects.get_or_create(user=request.user)[0]
            if 'next' in request.GET:
                if preference.include_deleted_students:
                    students = Student.objects.order_by('last_name','first_name')
                else:
                    students = Student.objects.filter(is_active=True).order_by('last_name','first_name')
            elif 'previous' in request.GET:
                if preference.include_deleted_students:
                    students = Student.objects.order_by('-last_name','-first_name')
                else:
                    students = Student.objects.filter(is_active=True).order_by('-last_name','-first_name')
            for student in students:
                if found:
                    return HttpResponseRedirect('/sis/view_student/' + str(student.id))
                if student == current_student:
                    found = True

    if request.method == 'POST':
        form = StudentLookupForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect('/sis/view_student/' + str(form.cleaned_data['student'].id))

    profile = UserPreference.objects.get_or_create(user=request.user)[0]

    if id:
        student = get_object_or_404(Student, pk=id)
    else:
        messages.warning(request, 'No Student Selected')
        return render_to_response('sis/view_student.html', {
            'include_inactive': profile.include_deleted_students,
        }, RequestContext(request, {}),)

    today = date.today()
    emergency_contacts = student.emergency_contacts.all()
    siblings = student.siblings.all()
    numbers = student.studentnumber_set.all()

    # Schedule
    cal = Calendar()
    try:
        location = cal.find_student(student)
    except:
        location = None
        print >> sys.stderr, str(sys.exc_info()[0])
    # Guess the mp desired (current or next coming)
    schedule_days = None
    periods = None
    # look for the current mp first
    current_mp = MarkingPeriod.objects.filter(start_date__lte=today, end_date__gte=today).order_by('-start_date')
    # nada? get the next mp (soonest-starting mp ending today or in the future)
    if not current_mp:
        current_mp = MarkingPeriod.objects.filter(end_date__gte=today).order_by('start_date')
    if current_mp:
        current_mp = current_mp[0]
        schedule_days, periods = cal.build_schedule(student, current_mp, include_asp=True)
    else:
        schedule_days = None
        periods = None

    # Discipline
    if 'ecwsp.discipline' in settings.INSTALLED_APPS:
        disciplines = student.studentdiscipline_set.all()
    else:
        disciplines = None

    #### CWSP related
    try:
        clientvisits = student.studentworker.clientvisit_set.all()
    except:
        clientvisits = None
    try:
        company_histories = student.studentworker.companyhistory_set.all()
    except:
        company_histories = None
    try:
        timesheets = student.studentworker.timesheet_set.exclude(Q(performance__isnull=True) | Q(performance__exact=''))
    except:
        timesheets = None
    try:
        if request.user.has_perm("sis.view_mentor_student"):
            student_interactions = student.studentworker.studentinteraction_set.all()
        else:
            student_interactions = None
    except:
        student_interactions = None
    try:
        supervisors = student.studentworker.placement.contacts.all()
    except:
        supervisors = None
    ########################################################################

    #Grades
    years = SchoolYear.objects.filter(markingperiod__coursesection__courseenrollment__user=student).distinct()
    from ecwsp.grades.models import Grade
    for year in years:
        year.mps = MarkingPeriod.objects.filter(coursesection__courseenrollment__user=student, school_year=year).distinct().order_by("start_date")
        year.course_sections = CourseSection.objects.filter(courseenrollment__user=student, course__graded=True, marking_period__school_year=year).distinct()
        for course_section in year.course_sections:
            # Too much logic for the template here, so just generate html.
            course_section.grade_html = ""
            for marking_period in year.mps:
                try:
                    course_section.grade_html += '<td> %s </td>' % (
                        Grade.objects.get(student=student, course_section=course_section, marking_period=marking_period).get_grade(),)
                except:
                    course_section.grade_html += '<td> </td>'
            try:
                course_section.grade_html += '<td> %s </td>' % (unicode(course_section.courseenrollment_set.get(user=student).grade),)
            except CourseEnrollment.DoesNotExist:
                course_section.grade_html += '<td></td>'

        # Attendance
        if 'ecwsp.attendance' in settings.INSTALLED_APPS:
            attendances = student.student_attn.filter(date__range=(year.start_date, year.end_date))
            year.attendances = attendances
            year.attendance_tardy = attendances.filter(status__tardy=True).count()
            year.attendance_absense = attendances.filter(status__absent=True).count()
            year.attendance_absense_with_half = year.attendance_absense + float(attendances.filter(status__half=True).count()) / 2
            year.total = year.get_number_days()
            year.present = year.total - year.attendance_tardy - year.attendance_absense_with_half

    #Standard Tests
    from ecwsp.administration.models import Configuration
    if 'ecwsp.standard_test' in settings.INSTALLED_APPS:
        from ecwsp.standard_test.models import StandardCategory, StandardCategoryGrade, StandardTest, StandardTestResult
        standard_tests = StandardTestResult.objects.filter(student=student)
    else:
        standard_tests = None

    return render_to_response('sis/view_student.html', {
        'date':today,
        'student':student,
        'emergency_contacts': emergency_contacts,
        'siblings': siblings,
        'numbers':numbers,
        'location':location,
        'disciplines':disciplines,
        'student_interactions': student_interactions,
        'clientvisits':clientvisits,
        'supervisors':supervisors,
        'company_histories':company_histories,
        'timesheets':timesheets,
        'years': years,
        'current_mp': current_mp,
        'schedule_days':schedule_days,
        'periods': periods,
        'include_inactive': profile.include_deleted_students,
        'tests': standard_tests
    }, RequestContext(request, {}),)

@permission_required('sis.change_student')
def increment_year(request):
    subtitle = "You can use this tool to change school years. It will change students year (fresh, soph, etc) and graudate as needed. "\
        "There will be confirmation screen before any changes are made."
    message = "Select the school year you wish to make active"
    form = YearSelectForm()
    if request.POST:
        form = YearSelectForm(request.POST)
        if form.is_valid():
            year = form.cleaned_data['school_year']
            return HttpResponseRedirect(reverse(increment_year_confirm, args=[year.id]))
    return render_to_response('sis/generic_form.html', {'subtitle': subtitle, 'form':form, 'msg': message}, RequestContext(request, {}),)


class StudentViewDashletView(generic.DetailView):
    model = Student
    template_name = 'sis/view_student_dashlet.html'

    @method_decorator(permission_required('sis.view_student'))
    def dispatch(self, *args, **kwargs):
        return super(StudentViewDashletView, self).dispatch(*args, **kwargs)


@transaction.atomic
def increment_year_confirm(request, year_id):
    """ Show user a preview of what increment year will do before making it
    """
    students = Student.objects.filter(is_active=True)
    subtitle = "Are you sure you want to make the following changes?"
    msg = "You can always change some manually later if you want to hold them back a year. Maybe you want to open them in new tabs now."
    year = get_object_or_404(SchoolYear, pk=year_id)
    school_last_year = GradeLevel.objects.order_by('-id')[0].id
    if request.POST:
        year.active_year = True
        year.save()
        for student in students:
            if student.class_of_year:
                new_year = student.get_year(year)
                if not new_year:
                    student.graduate_and_create_alumni()
                else:
                    student.year = new_year
                    student.save()
        messages.success(request, 'Successfully incremented student years!')
        return HttpResponseRedirect(reverse('admin:sis_student_changelist'))

    old_active_year = SchoolYear.objects.get(active_year = True)
    item_list = ["Change active year from %s to %s" % (old_active_year, year)]
    for student in students:
        row = None
        if student.class_of_year:
            new_year = student.get_year(year)
            if not new_year:
                row = '<a target="_blank" href="/admin/sis/student/%s">%s</a> (%s) - Graduate and mark inactive.' % (student.id, unicode(student), unicode(student.year))
                if 'ecwsp.alumni' in settings.INSTALLED_APPS:
                    row += ' Also make an alumni record.'
            else:
                try:
                    row = '<a target="_blank" href="/admin/sis/student/%s">%s</a> (%s) - Make a %s.' % (student.id, unicode(student), unicode(student.year), new_year)
                except SchoolYear.DoesNotExist:
                    pass
        if row:
            item_list += [mark_safe(row)]

    return render_to_response('sis/list_with_confirm.html', {'subtitle': subtitle, 'item_list':item_list, 'msg':msg}, RequestContext(request, {}),)


class SpaView(TemplateView):
    """ Use this for all Single Page Applications
    with angular. Shouldn't need to extend it
    but it could be done.
    """
    template_name = "spa.html"
