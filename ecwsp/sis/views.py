#   Copyright 2011 David M Burke
#   Author David M Burke <david@burkesoftware.com>
#   
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
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
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.forms.formsets import formset_factory
from django.forms.models import BaseModelFormSet, modelformset_factory
from django.db.models import Q, Sum, Count, get_model
from django.contrib.contenttypes.models import ContentType
from django.views.decorators.csrf import csrf_exempt
from django.utils.safestring import mark_safe

from ecwsp.administration.models import *
from ecwsp.sis.models import *
from ecwsp.sis.forms import *
from ecwsp.sis.report import *
from ecwsp.schedule.models import *
from ecwsp.schedule.calendar import *
from ecwsp.work_study.models import StudentWorker, TimeSheet
from ecwsp.sis.xlsReport import *

from ajax_select.fields import AutoCompleteSelectMultipleField, AutoCompleteSelectField
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
import xlwt
from tempfile import mkstemp
from datetime import date
import sys
import httpagentparser

@login_required
def user_preferences(request):
    profile = UserPreference.objects.get_or_create(user=request.user)[0]
    if request.POST:
        form = UserPreferenceForm(request.POST, instance=profile)
        if form.is_valid():
            form.cleaned_data['user'] = request.user
            form.save()
            messages.info(request, 'Successfully updated preferences')
            return HttpResponseRedirect(reverse('admin:index'))
    else:
        form = UserPreferenceForm(instance=profile)
    return render_to_response('sis/generic_form.html', {
        'form': form,
    }, RequestContext(request, {}),)

def get_fields_for_model(request):
    """ Get the related fields of a selected foreign key """
    model_class = ContentType.objects.get(id=request.GET['ct']).model_class()
    queryset = model_class.objects.filter(pk__in=request.GET['ids'].split(','))
    
    rel_name = request.POST['rel_name']
    related = model_class
    for item in rel_name.split('__'):
        related = getattr(related, item).field.rel.to
    
    model = related
    model_fields = model._meta.fields
    previous_fields = rel_name
    
    for field in model_fields:
        if hasattr(field, 'related'):
            if request.user.has_perm(field.rel.to._meta.app_label + '.view_' + field.rel.to._meta.module_name)\
            or request.user.has_perm(field.rel.to._meta.app_label + '.change_' + field.rel.to._meta.module_name):
                field.perm = True
    
    return render_to_response('sis/export_to_xls_related.html', {
        'model_name': model_class._meta.verbose_name,
        'model': model._meta.app_label + ":" + model._meta.module_name,
        'fields': model_fields,
        'previous_fields': previous_fields,
    }, RequestContext(request, {}),)
    
def admin_export_xls(request):
    model_class = ContentType.objects.get(id=request.GET['ct']).model_class()
    queryset = model_class.objects.filter(pk__in=request.GET['ids'].split(','))
    get_variables = request.META['QUERY_STRING']
    model_fields = model_class._meta.fields
    
    for field in model_fields:
        if hasattr(field, 'related'):
            if request.user.has_perm(field.rel.to._meta.app_label + '.view_' + field.rel.to._meta.module_name)\
            or request.user.has_perm(field.rel.to._meta.app_label + '.change_' + field.rel.to._meta.module_name):
                field.perm = True
    
    if 'xls' in request.POST:
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet(unicode(model_class._meta.verbose_name_plural))
        
        # Get field names from POST data
        fieldnames = []
        # request.POST reorders the data :( There's little reason to go through all
        # the work of reordering it right again when raw data is ordered correctly.
        for value in request.raw_post_data.split('&'):
            if value[:7] == "field__" and value[-3:] == "=on":
                fieldname = value[7:-3]
                app = fieldname.split('__')[0].split('%3A')[0]
                model = fieldname.split('__')[0].split('%3A')[1]
                # Server side permission check, edit implies view.
                if request.user.has_perm(app + '.view_' + model) or request.user.has_perm(app + '.change_' + model):
                    fieldnames.append(fieldname)
                
        # Title
        for i, field in enumerate(fieldnames):
            #ex field 'sis%3Astudent__fname'
            field = field.split('__')
            model = get_model(field[0].split('%3A')[0], field[0].split('%3A')[1])
            txt = ""
            for sub_field in field[1:-1]:
                txt += sub_field + " "
            txt += unicode(model._meta.get_field_by_name(field[-1])[0].verbose_name)
            worksheet.write(0,i, txt)
        
        # Data
        for ri, row in enumerate(queryset): # For Row iterable, data row in the queryset
            for ci, field in enumerate(fieldnames): # For Cell iterable, field, fields
                try:
                    field = field.split('__')
                    data = getattr(row, field[1])
                    for sub_field in field[2:]:
                        data = getattr(data, sub_field)
                    worksheet.write(ri+1, ci, unicode(data))
                except: # In case there is a None for a referenced field
                    pass 
        
        # Boring file handeling crap
        fd, fn = tempfile.mkstemp()
        os.close(fd)
        workbook.save(fn)
        fh = open(fn, 'rb')
        resp = fh.read()
        fh.close()
        response = HttpResponse(resp, mimetype='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename=%s.xls' % \
              (unicode(model_class._meta.verbose_name_plural),)
        return response
    
    return render_to_response('sis/export_to_xls.html', {
        'model_name': model_class._meta.verbose_name,
        'model': model_class._meta.app_label + ":" +  model_class._meta.module_name,
        'fields': model_fields,
        'get_variables': get_variables,
    }, RequestContext(request, {}),)



@login_required
def index(request):
    """if student, redirect them to timesheet.  if faculty allow this page
    """
    if request.user.groups.filter(Q(name='faculty') | Q(name='viewer')).count() > 0:
        try:
            # Warn users of IE and Firefox < 4.0 they are not supported
            ua = request.META['HTTP_USER_AGENT']
            browser_name = httpagentparser.detect(ua)['browser']['name']
            browser_version = httpagentparser.detect(ua)['browser']['version']
            if browser_name == "Microsoft Internet Explorer":
                messages.warning(request,
                    mark_safe('Warning Internet Explorer is not supported on the admin site. If you have any trouble, try using a standards compliant browser such as Firefox, Chrome, Opera, or Safari.'))
            elif browser_name == "Firefox" and int(browser_version[0]) < 4 :
                messages.warning(request, 'Warning, your version of Firefox is out of date. Please upgrade.')
        except:
            pass    
        return HttpResponseRedirect('/admin')
    elif request.user.groups.filter(Q(name='students')).count() > 0:
        from ecwsp.work_study.views import student_timesheet
        return student_timesheet(request)
    elif request.user.groups.filter(Q(name='company')).count() > 0:
        from ecwsp.work_study.views import supervisor_dash
        return supervisor_dash(request)
    else:
        return render_to_response('base.html', {'msg': "Not authorized", 'request': request,}, RequestContext(request, {}))

@user_passes_test(lambda u: u.groups.filter(name='registrar').count() > 0 or u.is_superuser, login_url='/')
def import_everything(request):
    if request.POST:
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            from ecwsp.sis.importer import *
            importer = Importer(request.FILES['file'], request.user)
            msg = ""
            msg_to_add, filename = importer.magic_import_everything()
            msg += msg_to_add
            form = UploadFileForm()
            return render_to_response('upload.html', {'form': form, 'msg': msg, 'error_filename':filename, 'request': request,})
        else:
            return render_to_response('upload.html', {'form': form, 'request': request,})
    form = UploadFileForm()
    return render_to_response('upload.html', {'form': form, 'request': request,}, RequestContext(request, {}))


@user_passes_test(lambda u: u.groups.filter(name='registrar').count() > 0 or u.is_superuser, login_url='/')    
def import_standardtestresult(request):
    if request.POST:
        form = UploadStandardTestResultForm(request.POST, request.FILES)
        if form.is_valid():
            from sis.importer import *
            importer = Importer(request.FILES['file'], request.user)
            msg = ""
            msg_to_add, filename = importer.import_just_standard_test(form.cleaned_data['test'])
            msg += msg_to_add
            form = UploadStandardTestResultForm()
            return render_to_response('upload.html', {'form': form, 'msg': msg, 'error_filename':filename, 'request': request,})
        else:
            return render_to_response('upload.html', {'form': form, 'request': request,})
    form = UploadStandardTestResultForm()
    return render_to_response('upload.html', {'form': form, 'request': request,}, RequestContext(request, {}))
    

@user_passes_test(lambda u: u.has_perm("sis.view_student"), login_url='/')    
def photo_flash_card(request, year=None):
    students = Student.objects.filter(inactive=False)
    grade_levels = GradeLevel.objects.all()
    try:
        if request.POST:
            form = StudentLookupForm(request.POST, request.FILES)
            if form.is_valid():
                id = form.cleaned_data['student']
            else:
                id = students.order_by('?')[0].pk
        else:
            form = StudentLookupForm()
            if year:
                id = students.filter(year=GradeLevel.objects.get(id=year)).order_by('?')[0].pk
            else:
                id = students.order_by('?')[0].pk
        student = Student.objects.filter(inactive=False).get(pk=id)
    except:
        messages.error(request, 'Student not found')
        return HttpResponseRedirect(reverse('admin:index'))
    return render_to_response('sis/flashcard.html', {'form': form, 'student_name': student, 'grade_levels':grade_levels, 'student_img': student.pic.url_530x400, 'request': request}, RequestContext(request, {}))

@user_passes_test(lambda u: u.has_perm("sis.view_student"), login_url='/')  
def transcript_nonofficial(request, id):
    student = Student.objects.filter(id=id)
    template = Template.objects.get_or_create(name="Transcript Nonoffical")[0]
    if template.file:
        template = template.file.path
        format = 'pdf'
        options = {
            'date': date.today(),
            'student': student,
        }
        return pod_report_grade(template, transcript=True, options=options, students=student, format=format)
        
    messages.info(request, 'Please upload a templated called "Transcript Nonoffical"')
    return HttpResponseRedirect(reverse('admin:index'))
    
    form = StudentReportWriterForm(request.POST, request.FILES)
    data = form.cleaned_data
    if data['template']:
        # use selected template
        template = data['template']
        template = template.file.path
    else:
        # or use uploaded template, saving it to temp file
        template = request.FILES['upload_template']
        tmpfile = mkstemp()[1]
        f = open(tmpfile, 'wb')
        f.write(template.read())
        f.close()
        template = tmpfile
    format = UserPreference.objects.get_or_create(user=request.user)[0].get_format(type="document")
    if 'pod_report_transcript' in request.POST:
        transcript = True
    else:
        transcript = False
    return pod_report_grade(template, transcript=transcript, options=data, students=form.get_students(data), format=format)


@user_passes_test(lambda u: u.groups.filter(name='registrar').count() > 0 or u.is_superuser, login_url='/')    
def school_report_builder_view(request, report=None):
    if request.method == 'POST':
        if 'thumbs_fresh' in request.POST:
            return student_thumbnail(request, GradeLevel.objects.get(id=9))
        elif 'thumbs_soph' in request.POST:
            return student_thumbnail(request, GradeLevel.objects.get(id=10))
        elif 'thumbs_jun' in request.POST:
            return student_thumbnail(request, GradeLevel.objects.get(id=11))
        elif 'thumbs_sen' in request.POST:
            return student_thumbnail(request, GradeLevel.objects.get(id=12))
        elif 'pod_report' in request.POST:
            form = StudentReportWriterForm(request.POST, request.FILES)
            if form.is_valid():
                data = form.cleaned_data
                if data['template']:
                    # use selected template
                    template = data['template']
                    template = template.file.path
                else:
                    # or use uploaded template, saving it to temp file
                    template = request.FILES['upload_template']
                    tmpfile = mkstemp()[1]
                    f = open(tmpfile, 'wb')
                    f.write(template.read())
                    f.close()
                    template = tmpfile
                format = UserPreference.objects.get_or_create(user=request.user)[0].get_format(type="document")
                return pod_report_all(template, options=data, students=form.get_students(data), format=format)
            else:
                return render_to_response('sis/reportBuilder.html', {'request':request, 'form':form})
    else:
        form = StudentReportWriterForm()
        form.fields['template'].queryset = Template.objects.filter(general_student=True)
        return render_to_response('sis/reportBuilder.html', {'request':request, 'form':form}, RequestContext(request, {}))


@user_passes_test(lambda u: u.has_perm('sis.view_student'), login_url='/')      
def student_thumbnail(request, year):
    response = HttpResponse(mimetype="application/pdf")
    response['Content-Disposition'] = 'attachment; filename=%s' % "thumbnails.pdf"
    
    c = canvas.Canvas(response, pagesize=letter)  
    
    students = Student.objects.filter(year=year).order_by('lname', 'fname')
    xsize = 6*cm
    ysize = 4.5*cm
    dx = .7*cm + xsize    #space between each pic
    dy = 2*cm + ysize
    x = 1*cm            # starting locations
    y = 1*cm
    xn = 0                # counters
    yn = 0
    paper_height = 23*cm
    for stu in students:
        try:    
            if stu.pic:
                c.drawImage(unicode(settings.MEDIA_ROOT[:-7] + unicode(stu.pic.url_530x400)), x, paper_height - (y-.4*cm), xsize, ysize, preserveAspectRatio=True)
            else:
                c.drawString(x, paper_height - (y+.5*cm), "No Image")
            c.drawString(x, paper_height - y, unicode(stu))
            if xn < 2:
                x += dx
                xn += 1
            else:
                x = 1*cm
                xn = 0
                if yn < 3:
                    y += dy
                    yn += 1
                else:
                    y = 1*cm
                    yn = 0
                    c.showPage()  
        except:
            print >> sys.stderr, str(sys.exc_info()[0])
    c.showPage()  
    c.save()
    return response


def logout_view(request):
    logout(request)
    return render_to_response('base.html', {'msg': "You have been logged out.",}, RequestContext(request, {}))


def teacher_attendance_which(request, type):
    teacher = Faculty.objects.get(username=request.user.username)
    if type == "homeroom":
        today = date.today()
        courses = Course.objects.filter(homeroom=True, teacher=teacher, marking_period__start_date__lte=today, marking_period__end_date__gte=today)
    elif type == "asp":
        courses = Course.objects.filter(asp=True, teacher=teacher)
    return render_to_response('sis/teacher_attendance_which.html', {'request': request, 'type':type, 'courses': courses}, RequestContext(request, {}))


@user_passes_test(lambda u: u.groups.filter(name='teacher').count() > 0 or u.is_superuser, login_url='/')    
def teacher_attendance(request, course=None, type="homeroom"):
    """ Take attendance.
    course: if known. If teacher only has one course then this will be selected automatically
    type: homeroom (default) or asp """
    try:
        teacher = Faculty.objects.get(username=request.user.username)
    except:
        messages.info(request, 'You do not exists as a Teacher. Tell an administrator to create a teacher with your username. Ensure "teacher" is checked off.')
        return HttpResponseRedirect(reverse('admin:index'))
    if not course:
        today = date.today()
        if type == "homeroom":
            courses = Course.objects.filter(homeroom=True, teacher=teacher, marking_period__start_date__lte=today, marking_period__end_date__gte=today)
            if courses.count() > 1:
                return teacher_attendance_which(request, type)
            elif courses.count() == 1:
                course = courses[0]
            else:
                messages.info(request, 'You are a teacher, but have no courses with attendance. This may also occur if the course is not set to the current marking period.')
                return HttpResponseRedirect(reverse('admin:index'))
        elif type == "asp":
            if Course.objects.filter(asp=True, teacher=teacher).count() > 1:
                return teacher_attendance_which(request, type)
            elif Course.objects.filter(asp=True, teacher=teacher).count() == 0:
                messages.info(request, 'You are a teacher, but have no ASP courses with attendance.')
                return HttpResponseRedirect(reverse('admin:index'))
            course = Course.objects.get(asp=True, teacher=teacher)
    else:
        course = Course.objects.get(id=course)
        if course.teacher != teacher:
            messages.info(request, 'You are not the teacher of this course!')
            return HttpResponseRedirect(reverse('admin:index'))
    students = course.get_attendance_students()
    
    if type == "homeroom":
        asp = False
    elif type == "asp":
        asp = True
    if AttendanceLog.objects.filter(date=date.today(), user=request.user, course=course, asp=asp).count() > 0:
        readonly = True
    else:
        readonly = False
    
    if type == "homeroom":
        AttendanceFormset = modelformset_factory(StudentAttendance, form=StudentAttendanceForm, extra=students.exclude(student_attn__date=date.today()).count())
    elif type == "asp":
        AttendanceFormset = modelformset_factory(ASPAttendance, form=ASPAttendanceForm, extra=students.exclude(aspattendance__date=date.today()).count())
    if request.method == 'POST':
        formset = AttendanceFormset(request.POST)
        if formset.is_valid():
            for form in formset.forms:
                object = form.save()
                if type == "asp":
                    if object.status == "P":
                        object.delete()
                    else:
                        object.course = course
                        object.save()
                LogEntry.objects.log_action(
                    user_id         = request.user.pk, 
                    content_type_id = ContentType.objects.get_for_model(object).pk,
                    object_id       = object.pk,
                    object_repr     = unicode(object), 
                    action_flag     = ADDITION
                )
            AttendanceLog(user=request.user, date=date.today(), course=course, asp=asp).save()
            messages.success(request, 'Attendance recorded')
            return HttpResponseRedirect(reverse('admin:index'))
        else:
            initial = []
            enroll_notes = []
            msg = ""
            for student in students:
                if type == "homeroom":
                    attendances = StudentAttendance.objects.filter(date=date.today(), student=student)
                else:
                    attendances = ASPAttendance.objects.filter(date=date.today(), student=student)
                if attendances.count():
                    # already exists, just make read only
                    msg += '<br/>%s is already marked %s %s.' % (student, attendances[0].status, attendances[0].notes)
                else:
                    status = None
                    if type == "asp":
                        # check for school attendance data
                        if student.student_attn.filter(date=date.today(), status__absent=True).count():
                            status = "S"
                    initial.append({'student': student.id, 'status': status, 'notes': None, 'date': date.today() })
                    note = student.courseenrollment_set.filter(course=course)[0].attendance_note
                    if note: enroll_notes.append(unicode(note))
                    else: enroll_notes.append("") 
    else:
        initial = []
        enroll_notes = []
        msg = ""
        for student in students:
            if type == "homeroom":
                attendances = StudentAttendance.objects.filter(date=date.today(), student=student)
            else:
                attendances = ASPAttendance.objects.filter(date=date.today(), student=student)
            if attendances.count():
                # already exists, just make read only
                try:
                    msg += '<br/>%s is already marked %s %s.' % (student, attendances[0].status, attendances[0].notes)
                except: pass
            else:
                status = None
                if type == "asp":
                    # check for school attendance data
                    if student.student_attn.filter(date=date.today(), status__absent=True).count():
                        status = "S"
                initial.append({'student': student.id, 'status': status, 'notes': None, 'date': date.today() })
                note = student.courseenrollment_set.filter(course=course)[0].attendance_note
                if note: enroll_notes.append(unicode(note))
                else: enroll_notes.append("")
        formset = AttendanceFormset(initial=initial, queryset=StudentAttendance.objects.none())
    
    i = 0
    number = []
    if type == "homeroom":
        students = students.exclude(student_attn__date=date.today())
    else:
        students = students.exclude(aspattendance__date=date.today())
    for form in formset.forms:
        form.enroll_note = enroll_notes[i]
        form.student_display = students[i]
        number.append(i)
        i += 1
    return render_to_response('sis/teacher_attendance.html', {'request': request, 'msg': msg, 'readonly': readonly, 'formset': formset, 'number': number})


@user_passes_test(lambda u: u.has_perm('sis.change_studentattendance')) 
def teacher_submissions(request):
    logs = AttendanceLog.objects.filter(date=date.today(), asp=False)
    homerooms = Course.objects.filter(homeroom=True)
    homerooms = homerooms.filter(marking_period__school_year__active_year=True)
    homerooms = homerooms.filter(coursemeet__day__contains=date.today().isoweekday()).distinct()
    submissions = []
    for homeroom in homerooms:
        submission = {}
        submission['homeroom'] = homeroom
        submission['teacher'] = homeroom.teacher
        teacher_user, created = User.objects.get_or_create(username=homeroom.teacher.username)
        log = AttendanceLog.objects.filter(date=date.today(), user=teacher_user)
        if log.count() > 0:
            submission['submitted'] = "Yes"
        else:
            submission['submitted'] = "No"
        submissions.append(submission)
    return render_to_response('sis/teacher_submissions.html', {'request': request, 'submissions': submissions})
    
    
@user_passes_test(lambda u: u.has_perm('sis.change_aspattendance')) 
def asp_submissions(request):
    logs = AttendanceLog.objects.filter(date=date.today(), asp=True)
    courses = Course.objects.filter(
        asp=True,
        coursemeet__day__contains=date.today().isoweekday()
    ).distinct()
    submissions = []
    for course in courses:
        submission = {}
        submission['homeroom'] = course
        if course.teacher:
            submission['teacher'] = course.teacher
            submission['id'] = course.id
            teacher_user, created = User.objects.get_or_create(username=course.teacher.username)
            if logs.filter(user=teacher_user).count():
                submission['submitted'] = "Yes"
            else:
                submission['submitted'] = "No"
        else:
            submission['submitted'] = "No teacher!"
        submissions.append(submission)
    courses = Course.objects.filter(
        asp=True,
        coursemeet__day__contains=date.today().isoweekday()
    )
    return render_to_response('sis/asp_submissions.html', {'request': request, 'submissions': submissions, 'courses': courses})


class BaseDisciplineFormSet(BaseModelFormSet):
    def add_fields(self, form, index):
        super(BaseDisciplineFormSet, self).add_fields(form, index)
        form.fields["students"] = AutoCompleteSelectMultipleField('dstudent')
        form.fields['comments'].widget = forms.TextInput(attrs={'size':'50'})
        form.fields['date'].widget = adminwidgets.AdminDateWidget()
                

@user_passes_test(lambda u: u.groups.filter(name='faculty').count() > 0 or u.is_superuser, login_url='/')    
def enter_discipline(request):
    DisciplineFormSet = modelformset_factory(StudentDiscipline, extra=5, formset=BaseDisciplineFormSet)
    if request.method == 'POST':
        formset = DisciplineFormSet(request.POST)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Discipline records added')
            if 'addmore' in request.POST:
                formset = DisciplineFormSet(queryset=StudentDiscipline.objects.none())
                return render_to_response('sis/enter_discipline.html', {'request': request, 'formset': formset, 'messages': messages.get_messages(request)})
            else:
                return HttpResponseRedirect(reverse('admin:sis_studentdiscipline_changelist'))
        else:
            return render_to_response('sis/enter_discipline.html', {'request': request, 'formset': formset})
    else:
        formset = DisciplineFormSet(queryset=StudentDiscipline.objects.none())
    return render_to_response('sis/enter_discipline.html', {'request': request, 'formset': formset})


@user_passes_test(lambda u: u.groups.filter(name='faculty').count() > 0 or u.is_superuser, login_url='/') 
def view_discipline(request):
    form = DisciplineViewForm()
    form.back = "/admin/sis/studentdiscipline/"
    return render_to_response('sis/view_form.html', {'request': request, 'form': form})


@user_passes_test(lambda u: u.groups.filter(name='faculty').count() > 0 or u.is_superuser, login_url='/') 
def discipline_report(request, student_id):
    """Generate a complete report of a student's discipline history
    """
    template, created = Template.objects.get_or_create(name="Discipline Report")
    
    school_name, created = Configuration.objects.get_or_create(name="School Name")
    school_name = school_name.value
    
    student = Student.objects.get(id=student_id)
    disc = StudentDiscipline.objects.filter(students=student)
    
    data = get_default_data()
    data['disciplines'] = disc
    data['school_year'] = SchoolYear.objects.get(active_year=True)
    data['student'] = student
    data['student_year'] = student.year
    
    return pod_save("disc_report", ".odt", data, template.file.path)
    

@user_passes_test(lambda u: u.groups.filter(name='faculty').count() > 0 or u.is_superuser, login_url='/')    
def discipline_list(request, type="doc", start_date=False, end_date=False):
    template = Template.objects.get_or_create(name="Discipline Daily List")[0].get_template_path(request)
    if not template:
        return HttpResponseRedirect(reverse('admin:index'))
    
    data={}
    if start_date:
        discs = StudentDiscipline.objects.filter(date__range=(start_date, end_date))
    else:
        discs = StudentDiscipline.objects.filter(date=date.today())
    
    data['disciplines'] = []
    for disc in discs:
        for student in disc.students.all():
            data['disciplines'].append(student)
    
    return pod_report(template, data, "Discipline List")


@user_passes_test(lambda u: u.groups.filter(name='faculty').count() > 0 or u.is_superuser, login_url='/')    
def discipline_report_view(request):
    form = DisciplineStudentStatistics()
    if request.method == 'POST':
        form = DisciplineStudentStatistics(request.POST)
        if form.is_valid():
            data = []
            start, end = form.get_dates()
            if 'student' in request.POST:
                students = Student.objects.all()
                if not form.cleaned_data['include_deleted'] :
                    students = students.exclude(inactive=True)
                if form.cleaned_data['order_by'] == "Year":
                    students = students.order_by('year')
                subtitles = ["Student",]
                titles = ["","Infractions",]
                for infr in PresetComment.objects.all():
                    titles.append("")
                titles.pop()
                titles.append("Actions")
                for infr in PresetComment.objects.all():
                    subtitles.append(unicode(infr))
                for action in DisciplineAction.objects.all():
                    subtitles.append(unicode(action))
                    titles.append("")
                titles.pop()
                data.append(subtitles)
                
                pref = UserPreference.objects.get_or_create(user=request.user)[0]
                for student in students:
                    disciplines = student.get_disciplines()
                    disciplines = disciplines.filter(date__range=(start, end))
                    stats = [unicode(student),]
                    
                    add = True
                    for infr in PresetComment.objects.all():
                        number = disciplines.filter(infraction=infr, students=student).count()
                        stats.append(number)
                        # check for filter
                        if form.cleaned_data['infraction'] == infr:
                            infraction_discipline = disciplines.filter(infraction=form.cleaned_data['infraction'])
                            if number < form.cleaned_data['minimum_infraction']:
                                add = False
                    for action in DisciplineAction.objects.all():
                        actions = disciplines.filter(disciplineactioninstance__action=action, students=student).count()
                        stats.append(actions)
                        # check for filter
                        if form.cleaned_data['action'] == action:
                            if actions < form.cleaned_data['minimum_action']:
                                add = False
                         
                    pref.get_additional_student_fields(stats, student, students, titles)
                    if add: data.append(stats)
                
                report = xlsReport(data, titles, "disc_stats.xls", heading="Discipline Stats")
                
                # By Teacher
                data = []
                titles = ['teacher']
                for action in DisciplineAction.objects.all():
                    titles.append(action)
                
                teachers = Faculty.objects.filter(studentdiscipline__isnull=False).distinct()
                disciplines = StudentDiscipline.objects.filter(date__range=(start, end))
                
                for teacher in teachers:
                    row = [teacher]
                    for action in DisciplineAction.objects.all():
                        row.append(disciplines.filter(teacher=teacher, action=action).count())
                    data.append(row)
                
                report.addSheet(data, titles=titles, heading="By Teachers")
                return report.finish()
                
            elif 'aggr' in request.POST:
                disciplines = StudentDiscipline.objects.filter(date__range=(start, end))
                if form.cleaned_data['this_year']:
                    school_start = SchoolYear.objects.get(active_year=True).start_date
                    school_end = SchoolYear.objects.get(active_year=True).end_date
                    disciplines = disciplines.filter(date__range=(school_start, school_end))
                elif not form.cleaned_data['this_year'] and not form.cleaned_data['all_years']:
                    disciplines = disciplines.filter(date__range=(form.cleaned_data['date_begin'], form.cleaned_data['date_end']))
                
                stats = []
                titles = []
                for infr in PresetComment.objects.all():
                    titles.append(infr)
                    number = disciplines.filter(infraction=infr).count()
                    stats.append(number)
                
                for action in DisciplineAction.objects.all():
                    titles.append(action)
                    number = 0
                    for a in DisciplineActionInstance.objects.filter(action=action):
                        number += a.quantity
                    stats.append(number)
                    
                data.append(stats)
                report = xlsReport(data, titles, "disc_stats.xls", heading="Discipline Stats")
                return report.finish()
        else:
            return render_to_response('sis/disc_report.html', {'request': request, 'form': form})
    return render_to_response('sis/disc_report.html', {'request': request, 'form': form})

@user_passes_test(lambda u: u.groups.filter(name='faculty').count() > 0 or u.is_superuser, login_url='/')  
def attendance_report(request):
    form = AttendanceReportForm()
    daily_form = AttendanceDailyForm()
    lookup_form = AttendanceViewForm()
    if request.method == 'POST':
        if "daily" in request.POST:
            daily_form = AttendanceDailyForm(request.POST)
            if daily_form.is_valid():
                type = UserPreference.objects.get_or_create(user=request.user)[0].get_format(type="document")
                return daily_attendance_report(daily_form.cleaned_data['date'], daily_form.cleaned_data['include_private_notes'], type=type)
        elif 'studentlookup' in request.POST:
            lookup_form = AttendanceViewForm(request.POST)
            if lookup_form.is_valid():
                type = UserPreference.objects.get_or_create(user=request.user)[0].get_format(type="document")
                return attendance_student(lookup_form.cleaned_data['student'].id, all_years=lookup_form.cleaned_data['all_years'], order_by=lookup_form.cleaned_data['order_by'], include_private_notes=lookup_form.cleaned_data['include_private_notes'], type=type)
            else:
                return render_to_response('sis/attendance_report.html', {'request': request, 'form':form, 'daily_form': daily_form, 'lookup_form': lookup_form}); 
        else: 
            form = AttendanceReportForm(request.POST)
            if form.is_valid():
                attendances = StudentAttendance.objects.all()
                data = []
                titles = []
                attendances = attendances.filter(date__range=(form.get_dates()))
                if 'student' in request.POST: # by student
                    students = StudentWorker.objects.all()
                    if not form.cleaned_data['include_deleted']:
                        students = students.filter(inactive=False)
                    students = students.filter()
                    
                    titles.append("Student")
                    titles.append("Total Absences")
                    titles.append("Total Tardies")
                    for status in AttendanceStatus.objects.exclude(name="Present"):
                        titles.append(status)
                    pref = UserPreference.objects.get_or_create(user=request.user)[0]
                    students_absent = students.filter(student_attn__status__absent=True, student_attn__in=attendances).annotate(abs=Count('student_attn'))
                    students_tardy = students.filter(student_attn__status__tardy=True, student_attn__in=attendances).annotate(abs=Count('student_attn'))
                    attn_tardy = attendances.filter(status__tardy=True)
                    
                    students_each_total = {}
                    for status in AttendanceStatus.objects.exclude(name="Present"):
                        students_each_total[status.name] = students.filter(student_attn__status=status, student_attn__in=attendances).annotate(abs=Count('student_attn'))
                    
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
                            
                        if total_absent >= form.cleaned_data['filter_total_absences'] and total_tardy >= form.cleaned_data['filter_total_tardies']:
                            row.append( total_absent )
                            row.append( total_tardy )
                            for status in AttendanceStatus.objects.exclude(name="Present"):
                                count = 0
                                if student in students_each_total[status.name]:
                                    count = students_each_total[status.name].filter(id=student.id)[0].abs
                                row.append(count)
                                if form.cleaned_data['filter_status'] == status and attendances.filter(student=student, status=status).count() < form.cleaned_data['filter_count']:
                                    add = False
                            pref.get_additional_student_fields(row, student, students, titles)
                            if add: data.append(row)    
                    report = xlsReport(data, titles, "attendance_report.xls", heading="Attendance Report")
                    
                elif 'perfect_attendance' in request.POST:
                    form = AttendanceReportForm(request.POST)
                    if form.is_valid():
                        data = form.cleaned_data
                        template = Template.objects.get_or_create(name="Perfect attendance")[0]
                        template = template.file.path
                        
                        students = Student.objects.all()
                        perfect_students = []
                        if not form.cleaned_data['include_deleted']:
                            students = students.filter(inactive=False)
                        for student in students:
                            total_absent = attendances.filter(status__absent=True, student=student).count()
                            total_tardy = attendances.filter(status__tardy=True, student=student).count()
                            if not total_absent and not total_tardy:
                                perfect_students.append(student)
                        
                        format = UserPreference.objects.get_or_create(user=request.user)[0].get_format(type="document")
                        return pod_report_all(template, students=perfect_students, format=format)
                        
                elif 'attendance_daily_stat' in request.POST:
                    form = AttendanceReportForm(request.POST)
                    if form.is_valid():
                        days = AttendanceDailyStat.objects.filter(date__range=form.get_dates())
                        data = []
                        titles = ['Date', 'Present', 'Absent', 'Absent Percentage']
                        row = 3
                        for day in days:
                            # Formula C3/(B3+C3)
                            percentage = xlwt.Formula("C" + str(row) + "/(B" +str(row) + "+C" + str(row) + ')')
                            data.append([day.date, day.present, day.absent, percentage])
                            row += 1
                        report = xlsReport(data, titles, "attendance_daily_stats_report.xls", heading="Attendance Daily Stats")
                        
                else: # Aggregate report
                    stats = []
                    for status in AttendanceStatus.objects.exclude(name="Present"):
                        titles.append(status)
                        number = attendances.filter(status=status).count()
                        stats.append(number)
                    data.append(stats)
                    data.append([])
                    
                    students = Student.objects.filter(inactive=False).count()
                    absents = attendances.filter(status__absent=True).count()
                    days = SchoolYear.objects.get(active_year=True).get_number_days()
                    #percentage = 1.0 - float(absents) / (float(students) * float(days))
                    percentage = xlwt.Formula("1-(B6/(A6*C6))")
                    data.append(['Students', 'Total Absents', 'School days', 'Absent Percentage'])
                    data.append([students, absents, days, percentage])
                    
                    report = xlsReport(data, titles, "attendance_report.xls", heading="Attendance Report")
                return report.finish()
    return render_to_response('sis/attendance_report.html', {'form':form, 'daily_form': daily_form, 'lookup_form': lookup_form}, RequestContext(request, {}),);


@user_passes_test(lambda u: u.groups.filter(name='faculty').count() > 0 or u.is_superuser, login_url='/')
def student_page_redirect(request, id):
    """ Redirects user to highest level of permission they have for a student """
    try: from work_study.models import StudentWorker
    except: pass
    if request.user.has_perm(StudentWorker):
        return HttpResponseRedirect(reverse('admin:work_study_studentworker_change', args=(id,)))
    return HttpResponseRedirect(reverse('admin:sis_student_change', args=(id,)))


@user_passes_test(lambda u: u.groups.filter(name="registrar").count() or u.is_superuser, login_url='/')   
def grade_report(request):
    form = StudentGradeReportWriterForm()
    mp_form = MarkingPeriodForm()
    
    if request.method == 'POST':
        if 'student_grade' in request.POST:
            form = StudentGradeReportWriterForm(request.POST, request.FILES)
            if form.is_valid():
                data = form.cleaned_data
                if data['template']:
                    # use selected template
                    template = data['template']
                    template_path = template.file.path
                    report_card = template.report_card
                    transcript = template.transcript
                else:
                    # or use uploaded template, saving it to temp file
                    template = request.FILES['upload_template']
                    tmpfile = mkstemp()[1]
                    f = open(tmpfile, 'wb')
                    f.write(template.read())
                    f.close()
                    template_path = tmpfile
                    report_card = True
                    transcript = True
                format = UserPreference.objects.get_or_create(user=request.user)[0].get_format(type="document")
                return pod_report_grade(template_path, options=data, students=form.get_students(data), format=format, report_card=report_card, transcript=transcript)
                
        elif 'aggregate_grade_report' in request.POST:
            form = MarkingPeriodForm(request.POST)
            if form.is_valid():
                mps = form.cleaned_data['marking_period']
                data = []
                titles = ["Teacher", "Range", "No. Students", ""]
                for level in GradeLevel.objects.all():
                    titles += [level, ""]
                ranges = [['100', '90'], ['89.99', '80'], ['79.99', '70'], ['69.99', '60'], ['59.99', '50'], ['49.99', '0']]
                letter_ranges = ['P', 'F']
                for teacher in Faculty.objects.filter(course__marking_period__in=mps).distinct():
                    data.append([teacher])
                    grades = Grade.objects.filter(
                        marking_period__in=mps,
                        course__teacher=teacher,
                        student__inactive=False,
                        final=True,
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
                report = xlsReport(data, titles, "aggregate_grade_report.xls", heading="Teacher aggregate")
                
                passing = 70
                data = []
                titles = ['Grade']
                for dept in Department.objects.all():
                    titles.append(dept)
                    titles.append('')
                for level in GradeLevel.objects.all():
                    row = [level]
                    for dept in Department.objects.all():
                        fails = Grade.objects.filter(
                            marking_period__in=mps,
                            course__department=dept,
                            student__inactive=False,
                            student__year__in=[level],   # Shouldn't need __in. Makes no sense at all.
                            grade__lt=passing,
                            final=True,
                            override_final=False,
                        ).count()
                        total = Grade.objects.filter(
                            marking_period__in=mps,
                            course__department=dept,
                            student__inactive=False,
                            student__year__in=[level],
                            final=True,
                            override_final=False,
                        ).count()
                        if total:
                            percent = float(fails) / float(total)
                        else:
                            percent = 0
                        percent = ('%.2f' % (percent * 100,)).rstrip('0').rstrip('.')
                        row.append(fails)
                        row.append(percent)
                    data.append(row)
                report.addSheet(data, titles=titles, heading="Class Dept aggregate")
                return report.finish()
    form.fields['template'].queryset = Template.objects.filter(Q(report_card=True) | Q(transcript=True))
    return render_to_response('sis/grade_report.html', {'form':form, 'mp_form':mp_form}, RequestContext(request, {}),)
    
@user_passes_test(lambda u: u.has_perm("sis.view_student"), login_url='/')   
def view_student(request, id=None):
    student = None
    show_grades = False
    if request.method == 'POST':
        form = StudentLookupForm(request.POST)
        if form.is_valid():
            student = Student.objects.get(id=form.cleaned_data['student'].id)
    elif request.method == 'GET':
        try:
            form = StudentLookupForm(request.GET)
            if form.is_valid():
                student = Student.objects.get(id=form.cleaned_data['student'].id)
            if request.GET['show_grades']:
                show_grades = True
        except: pass
    if 'include_deleted' in request.GET:
        form = DeletedStudentLookupForm()
        include_deleted = True
    else:
        form = StudentLookupForm()
        include_deleted = False
    today = date.today()
    if student:
        emergency_contacts = student.emergency_contacts.all()
        siblings = student.siblings.all()
        cohorts = student.cohorts.all()
        numbers = student.studentnumber_set.all()
        
        # Schedule
        cal = Calendar()
        try:
            location = cal.find_student(student)
        except:
            location = None
            print >> sys.stderr, str(sys.exc_info()[0])
        # Guess the mp desired (current or next coming)
        current_mp = MarkingPeriod.objects.filter(end_date__gte=today).order_by('-start_date')
        if current_mp:
            current_mp = current_mp[0]
            schedule_days, periods = cal.build_schedule(student, current_mp, include_asp=True)
        else:
            schedule_days = None
            periods = None
        
        disciplines = student.studentdiscipline_set.all()
        attendances = student.student_attn.all()
        
        # Alumni
        if hasattr(student, 'alumni') and request.user.has_perm("alumni.view_alumni"):
            alumni = student.alumni
        else:
            alumni = None
        
        #### CWSP related
        try:
            clientvisits = student.studentworker.clientvisit_set.all()
            company_histories = student.studentworker.companyhistory_set.all()
            timesheets = student.studentworker.timesheet_set.exclude(Q(performance__isnull=True) | Q(performance__exact=''))
            if request.user.has_perm("sis.view_mentor_student"):
                student_interactions = student.studentworker.studentinteraction_set.all()
            else:
                student_interactions = None
        except:
            clientvisits = None
            company_histories = None
            timesheets = None
            student_interactions = None
        try:
            supervisors = student.studentworker.placement.contacts.all()
        except:
            supervisors = None
        ########################################################################
        
        years = SchoolYear.objects.filter(markingperiod__course__courseenrollment__user=student).distinct()
        for year in years:
            year.mps = MarkingPeriod.objects.filter(course__courseenrollment__user=student, school_year=year).distinct().order_by("start_date")
            year.courses = Course.objects.filter(courseenrollment__user=student, homeroom=False, marking_period__school_year=year).distinct()
            for course in year.courses:
                # Too much logic for the template here, so just generate html.
                course.grade_html = ""
                for mp in year.mps:
                    try:
                        course.grade_html += '<td> %s </td>' % (Grade.objects.get(student=student, final=True, course=course, marking_period=mp).get_grade(),)
                    except:
                        course.grade_html += '<td> </td>'
                course.grade_html += '<td> %s </td>' % (unicode(course.get_final_grade(student)),)
                
        return render_to_response('sis/view_student.html', {'form':form, 'show_grades':show_grades, 'date':today, 'student':student, 'emergency_contacts': emergency_contacts,
                                                        'siblings': siblings, 'numbers':numbers, 'location':location, 'disciplines':disciplines, 'attendances':attendances,
                                                        'student_interactions': student_interactions, 'clientvisits':clientvisits, 'supervisors':supervisors,
                                                        'company_histories':company_histories, 'timesheets':timesheets, 'years': years,
                                                        'include_deleted': include_deleted, 'current_mp': current_mp, 'schedule_days':schedule_days,
                                                        'alumni': alumni, 'periods': periods,}, RequestContext(request, {}),)
    return render_to_response('sis/view_student.html', {'form':form, 'include_deleted': include_deleted}, RequestContext(request, {}),)
