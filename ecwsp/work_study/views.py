from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import user_passes_test, permission_required
from django.contrib import messages
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.core import urlresolvers
from django.db.models import Q
from django.http import HttpResponse
from django import forms
from django.core.mail import EmailMessage
from django.db.models import Sum, Count, Avg
from django.forms.models import modelformset_factory
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.exceptions import ValidationError

from ecwsp.work_study.models import StudentWorker, Contact, TimeSheet, WorkTeam, Company, ClientVisit, StudentInteraction, CompContract
from ecwsp.work_study.models import PaymentOption, CompanyHistory, Attendance
from ecwsp.administration.models import Configuration, AccessLog
from ecwsp.work_study.forms import ChangeSupervisorForm, TimeSheetForm, ReportTemplateForm, DolForm, CompanyContactForm1
from ecwsp.work_study.forms import  CompanyContactForm2, CompanyContactForm3, ReportBuilderForm, AddSupervisor, QuickAttendanceForm
from ecwsp.sis.xl_report import XlReport
from ecwsp.work_study.reports import fte_by_day, fte_by_ind, fte_by_pay, am_route_attendance, gen_attendance_report_day, route_attendance
from ecwsp.work_study.reports import student_company_day_report
from ecwsp.sis.models import StudentNumber, SchoolYear
from ecwsp.sis.helper_functions import log_admin_entry
from ecwsp.sis.template_report import TemplateReport

#from itertools import *
from datetime import date
from datetime import datetime
import sys
import re
import logging
import os

days = (["Monday", "M"], ["Tuesday","T"], ["Wednesday","W"], ["Thursday","TH"], ["Friday", "F"])
class struct(object): pass


def supervisor_xls(request):
    comp = WorkTeam.objects.filter(login=request.user)[0]
    timesheets = TimeSheet.objects.filter(approved=True).filter(company=comp).order_by('student', 'date',)
    data = []
    titles = ["WorkTeam", "Student", "", "Date", "For Pay?", "Make up?", "Hours Worked", "Company Bill", "Performance", "Student Comment", "Supervisor Comment"]
    fileName = "Billing_Report"
    company_total = timesheets.aggregate(Sum('school_net'))
    data.append([comp.team_name, "", "", "", "", "", "", company_total['school_net__sum']])
    studenti = 0
    for timesheet in timesheets:
        data.append(["",
                     timesheet.student.first_name,
                     timesheet.student.last_name,
                     timesheet.date,
                     timesheet.for_pay,
                     timesheet.make_up,
                     timesheet.hours,
                     timesheet.school_net,
                     timesheet.performance,
                     timesheet.student_accomplishment,
                     timesheet.supervisor_comment,])
        studenti += 1
        if studenti == timesheets.filter(student__id__iexact=timesheet.student.id).count():
            stu_total = timesheets.filter(student__id__iexact=timesheet.student.id).aggregate(Sum('hours'), Sum('student_net'), Sum('school_net'))
            data.append(["", "", "", "Total", "", "", stu_total['hours__sum'], stu_total['school_net__sum']])
            studenti = 0

    report = XlReport(file_name="Company Billing")
    report.add_sheet(data, header_row=titles, title="Company Billing", heading="Company Billing")
    return report.as_download()


@user_passes_test(lambda u: u.groups.filter(name='students').first())
def student_timesheet(request):
    """ A student's timesheet. """
    try:
        this_student = StudentWorker.objects.get(username=request.user.username)
        comp_contacts = Contact.objects.filter(workteam=this_student.placement)
    except:
        return render_to_response(
            'base.html',
            {'msg': "Student or Company does not exist. Please notify a system admin if you believe this is a mistake."},
            RequestContext(request, {}))
    try:
        supervisor_name = u'{} {}'.format(
            this_student.primary_contact.fname,
            this_student.primary_contact.lname)
    except AttributeError:
        supervisor_name = "No Supervisor"
    if request.method == 'POST':
        form = TimeSheetForm(request.POST)
        # check to make sure hidden field POST data isn't tampered with
        if form.is_valid() and \
        (request.POST['company'] == str(this_student.placement.id)) and \
        (request.POST['student'] == str(this_student.id)):
            if this_student.primary_contact != form.cleaned_data['my_supervisor']:
                this_student.primary_contact = form.cleaned_data['my_supervisor']
                this_student.save()
                LogEntry.objects.log_action(
                    user_id         = request.user.pk,
                    content_type_id = ContentType.objects.get_for_model(this_student).pk,
                    object_id       = this_student.pk,
                    object_repr     = unicode(this_student),
                    action_flag     = CHANGE,
                    change_message  = "Changed supervisor to " + unicode(form.cleaned_data['my_supervisor'])
                )
            obj = form.save()
            show_comment_default = Configuration.get_or_default(name="work_study show commment default", default='True',help_text="").value
            if show_comment_default == 'True':
                obj.show_student_comments = True
                obj.save()
            log_admin_entry(request, obj, ADDITION, message='Student created timesheet')
            access = AccessLog()
            access.login = request.user
            access.ua = request.META['HTTP_USER_AGENT']
            access.ip = request.META['REMOTE_ADDR']
            access.usage = "Student submitted time sheet"
            access.save()
            return render_to_response(
                'base.html',
                {'student': True, 'msg': "Timesheet has been successfully submitted, your supervisor has been notified."},
                RequestContext(request, {}))
    else:
        initial_primary = None
        if hasattr(this_student,"primary_contact"):
            if this_student.primary_contact:
                initial_primary = this_student.primary_contact.id
        if Configuration.get_or_default('work_study_timesheet_initial_time', 'True').value == 'True':
            form = TimeSheetForm(initial={'student':this_student.id, 'company':this_student.placement.id, 'my_supervisor':initial_primary,
                'date': date.today, 'time_in': "9:30 AM", 'time_lunch': "12:00 PM", 'time_lunch_return': "1:00 PM", 'time_out': "5:00 PM"})
        else:
            form = TimeSheetForm(initial={'student':this_student.id, 'company':this_student.placement.id, 'my_supervisor':initial_primary,
                'date': date.today, 'time_in': "", 'time_lunch': "", 'time_lunch_return': "", 'time_out': ""})
    form.set_supers(comp_contacts)
    form.fields['performance'].widget.attrs['disabled'] = 'disabled'
    # Should for_pay be an option?
    pay, created = Configuration.objects.get_or_create(name="Allow for pay")
    if created:
        pay.value = "True"
        pay.save()
    if pay.value != "True" and pay.value != "true":
        form.fields['for_pay'].widget = forms.HiddenInput()

    return render_to_response('work_study/student_timesheet.html', {
        'student': True,
        'form': form,
        'supervisorName': supervisor_name,
        },RequestContext(request, {}))

def timesheet_delete(request):
    """first check if key is valid, this replaces the need for login.
    """
    key = request.GET.get('key', '')
    try:
        sheet = TimeSheet.objects.get(supervisor_key = key)
    except:
        return render_to_response(
            'base.html',
            {'supervisor': True,'msg': "Link not valid. Was this timesheet already approved?"},
            RequestContext(request, {}))
    sheet.delete()

    return supervisor_dash(request, "Deleted time card")

def approve(request):
    """ first check if key is valid, this replaces the need for login.
    """
    key = request.GET.get('key', '')
    try:
        sheet = TimeSheet.objects.get(supervisor_key = key)
    except:
        return render_to_response(
            'base.html',
            {'supervisor': True,'msg': "Link not valid. Was this timesheet already approved?"},
            RequestContext(request, {}))
    # valid key, check for post
    if request.method == 'POST':
        form = TimeSheetForm(request.POST, request.FILES, instance=sheet)
        if form.is_valid():
            sheet = form.save(commit=False)
            sheet.student.primary_contact = form.cleaned_data['my_supervisor']
            sheet.student.save()
            sheet.approved = True
            sheet.supervisor_key = key
            sheet.save()
            log_admin_entry(request, sheet, CHANGE, 'Supervisor approved timesheet using link (probably from email)')
            if sheet.show_student_comments:
                sheet.emailStudent()
            else:
                sheet.emailStudent(show_comment=False)
            return render_to_response('base.html', {'supervisor': True, 'msg':"Time Card Approved!"}, RequestContext(request, {}))
        else:
            comp_contacts = Contact.objects.filter(workteam=sheet.student.placement)
            form.set_supers(comp_contacts)
            return render_to_response('work_study/student_timesheet.html', {'supervisor': True,'approved': sheet.approved, 'form': form, \
                'studentName': sheet.student, 'supervisorName': sheet.student.primary_contact,}, RequestContext(request, {}))
    else:
        if sheet.student.primary_contact:
            initial_primary = sheet.student.primary_contact.id
        else: initial_primary = None
        form = TimeSheetForm(instance=sheet, initial={'edit':True, 'my_supervisor':initial_primary,})
        comp_contacts = Contact.objects.filter(workteam=sheet.student.placement)
        form.set_supers(comp_contacts)
        return render_to_response('work_study/student_timesheet.html', {'supervisor': True, 'approved': sheet.approved, 'form': form, \
            'studentName': sheet.student, 'supervisorName': sheet.student.primary_contact,}, RequestContext(request, {}))


@user_passes_test(lambda u: u.groups.filter(name='company').first())
def supervisor_dash(request, msg=""):
    """ Supervisor dashboard view to checking and making student time sheets
    """
    try:
        comp = WorkTeam.objects.filter(login=request.user)[0]
    except IndexError:
        return render_to_response(
            'base.html',
            {'msg': "You are a supervisor user but not linked to any specific company. Please notify administrator if you believe this is a mistake."},
            RequestContext(request, {}))
    if 'mass_approve' in request.POST:
        msg = "All checked time sheets approved"
        time_sheets = TimeSheet.objects.filter(company=comp).filter(approved=False)
        # for each post value
        for check in request.POST.values():
            # is it an id in the timesheet? Only check this companies timesheets
            for ts in time_sheets:
                if str(ts.id) == str(check):
                    ts.approved = True
                    ts.save()
                    log_admin_entry(request, ts, CHANGE,message='Supervisor mass approval')
    students = StudentWorker.objects.filter(placement=comp)
    time_sheets = TimeSheet.objects.filter(company=comp).filter(approved=False)
    TimeSheetFormSet = modelformset_factory(TimeSheet, fields=('approved',))
    time_sheets_approved_form = TimeSheetFormSet(queryset=time_sheets)
    try:
        access = AccessLog()
        access.login = request.user
        access.ua = request.META['HTTP_USER_AGENT']
        access.ip = request.META['REMOTE_ADDR']
        access.usage = "Supervisor Dash"
        access.save()
    except:
        print >> sys.stderr, "error creating access log"
    return render_to_response('work_study/supervisor_dash.html', {'supervisor': True, 'msg': msg, 'comp': comp, 'students': students, \
        'timeSheets': time_sheets, 'timeSheetsApprovedForm': time_sheets_approved_form}, RequestContext(request, {}))



@user_passes_test(lambda u: u.groups.filter(name='company').first())
def supervisor_view(request):
    """ ?
    """
    comp = WorkTeam.objects.filter(login=request.user)[0]
    time_sheets = TimeSheet.objects.filter(company=comp).filter(approved=True).order_by('date').reverse()[:100]
    return render_to_response(
        'work_study/supervisor_view.html',
        {'supervisor': True, 'timeSheets': time_sheets},
        RequestContext(request, {}))

@user_passes_test(lambda u: u.groups.filter(name='students').first())
def student_view(request):
    """ Student "dashboard"
    """
    try:
        this_student = StudentWorker.objects.get(username=request.user.username)
    except StudentWorker.DoesNotExist:
        return render_to_response(
            'base.html',
            {'msg': "Student does not exist or is not a Student Worker. Please notify a system admin if you believe this is a mistake."},
            RequestContext(request, {}))
    time_sheets = TimeSheet.objects.filter(student=this_student).order_by('date').reverse()[:100]
    return render_to_response(
        'work_study/student_view.html',
        {'timeSheets': time_sheets, 'student': this_student},
        RequestContext(request, {}))

@user_passes_test(lambda u: u.groups.filter(name='students').first())
def student_edit(request, tsid):
    """ Student edits own timesheet
    """
    thisStudent = StudentWorker.objects.get(username=request.user.username)
    timesheet = TimeSheet.objects.get(id=tsid)
    # Students can only edit their own NON approved time sheets
    if (timesheet.student != thisStudent or timesheet.approved):
        return render_to_response('base.html', {'student': True, 'msg': "This timesheet has already been approved. You cannot edit it."}, RequestContext(request, {}))

    compContacts = Contact.objects.filter(workteam=thisStudent.placement)
    try:
        supervisorName = thisStudent.primary_contact.fname + " " + thisStudent.primary_contact.lname
    except:
        supervisorName = "No Supervisor"
    if request.method == 'POST':
        form = TimeSheetForm(request.POST, request.FILES, instance=timesheet)
        # check to make sure hidden field POST data isn't tampered with
        if form.is_valid() and thisStudent.placement and (request.POST['company'] == str(thisStudent.placement.id)) and (request.POST['student'] == str(thisStudent.id)):
            if thisStudent.primary_contact != form.cleaned_data['my_supervisor']:
                thisStudent.primary_contact = form.cleaned_data['my_supervisor']
                thisStudent.save()
                LogEntry.objects.log_action(
                    user_id         = request.user.pk,
                    content_type_id = ContentType.objects.get_for_model(thisStudent).pk,
                    object_id       = thisStudent.pk,
                    object_repr     = unicode(thisStudent),
                    action_flag     = CHANGE,
                    change_message  = "Changed supervisor to " + unicode(form.cleaned_data['my_supervisor'])
                )
            obj = form.save()
            log_admin_entry(request,obj,CHANGE,message='Student changed timesheet')
            access = AccessLog()
            access.login = request.user
            access.ua = request.META['HTTP_USER_AGENT']
            access.ip = request.META['REMOTE_ADDR']
            access.usage = "Student edits time sheet"
            access.save()
            return render_to_response('base.html', {'student': True, 'msg': "Timesheet has be successfully updated, no additional notification sent."}, RequestContext(request, {}))
        else:
            return render_to_response('work_study/student_timesheet.html', {'student': True, 'form': form,
                'studentName': thisStudent, 'supervisorName': supervisorName,}, RequestContext(request, {}))
    else:
        if thisStudent.primary_contact: initial_primary = thisStudent.primary_contact.id
        else: initial_primary = None
        form = TimeSheetForm(instance=timesheet, initial={'edit':True, 'my_supervisor':initial_primary})
        form.set_supers(compContacts)
        return render_to_response('work_study/student_timesheet.html', {'student': True, 'form': form, 'studentName': thisStudent, \
            'supervisorName': supervisorName,}, RequestContext(request, {}))

@user_passes_test(lambda u: u.groups.filter(name='company').first())
def create_time_card(request, studentId):
    thisStudent = StudentWorker.objects.get(id = studentId)
    comp = WorkTeam.objects.filter(login=request.user)[0]
    compContacts = Contact.objects.filter(workteam=thisStudent.placement)
    if thisStudent.placement == comp:
        if request.method == 'POST':
            form = TimeSheetForm(request.POST, request.FILES)
            if form.is_valid():
                sheet = form.save(commit=False)
                if thisStudent.primary_contact != form.cleaned_data['my_supervisor']:
                    thisStudent.primary_contact = form.cleaned_data['my_supervisor']
                    thisStudent.save()
                    LogEntry.objects.log_action(
                        user_id         = request.user.pk,
                        content_type_id = ContentType.objects.get_for_model(thisStudent).pk,
                        object_id       = thisStudent.pk,
                        object_repr     = unicode(thisStudent),
                        action_flag     = CHANGE,
                        change_message  = "Changed supervisor to " + unicode(form.cleaned_data['my_supervisor'])
                    )
                sheet.approved = True
                sheet.genKey()
                sheet.save()
                log_admin_entry(request,sheet,ADDITION)
                if sheet.show_student_comments:
                    sheet.emailStudent()
                else:
                    sheet.emailStudent(show_comment=False)
                return supervisor_dash(request, "Timesheet submitted for " + thisStudent.first_name)
            else:
                form.set_supers(compContacts)
                if hasattr(thisStudent,"primary_contact") and thisStudent.primary_contact:
                    supervisorName = thisStudent.primary_contact.fname + " " + thisStudent.primary_contact.lname
                else:
                    supervisorName = comp.team_name
                return render_to_response('work_study/student_timesheet.html', {'supervisor': True,'new': True, 'form': form, 'studentName':\
                    thisStudent, 'supervisorName': supervisorName,}, RequestContext(request, {}))
        else:
            # if student
            if hasattr(thisStudent,"primary_contact") and thisStudent.primary_contact:
                supervisorName = thisStudent.primary_contact.fname + " " + thisStudent.primary_contact.lname
            else:
                supervisorName = comp.team_name

            # check if student already submitted time sheet today
            sheet = TimeSheet.objects.filter(student=thisStudent, date=datetime.now(), approved=False)
            if sheet:
                warning = True
                key = sheet[0].supervisor_key
            else:
                warning = False
                key = None

            if thisStudent.primary_contact: initial_primary = thisStudent.primary_contact.id
            else: initial_primary = None
            form = TimeSheetForm(initial={'student':thisStudent.id, 'company':thisStudent.placement.id, 'my_supervisor':initial_primary,
                'date': date.today, 'time_in': "9:30 AM", 'time_lunch': "12:00 PM", 'time_lunch_return': "1:00 PM", 'time_out': "5:00 PM"})
            form.set_supers(compContacts)
            return render_to_response('work_study/student_timesheet.html', {'warning': warning, 'key': key, 'supervisor': True,'new': True, \
                'form': form, 'studentName': thisStudent, 'supervisorName': supervisorName,}, RequestContext(request, {}))
    else:
        return HttpResponse("Access Denied")

def contracts_report():
    """ Returns xls report of all active companies and whether or not they
    submitted contracts """
    data = []
    titles = ["Company", "Contract?", "Date of last contract"]

    # companies with at least one active student
    companies = Company.objects.distinct()
    for company in companies:
        if company.compcontract_set.count() > 0:
            contract = "Yes"
            last = company.compcontract_set.all().order_by('-date')[0].date
        else:
            contract = "No"
            last = ""
        data.append([company.name, contract, last])

    report = XlReport(file_name="contract_report")
    report.add_sheet(data, header_row=titles, title="Contract Report", heading="Contract Report")
    return report.as_download()


@user_passes_test(lambda u: u.groups.filter(name='company').first() or u.is_superuser)
def change_supervisor(request, studentId):
    thisStudent = StudentWorker.objects.get(id = studentId)
    try:
        comp = WorkTeam.objects.filter(login=request.user)[0]
    except:
        comp = None
    if thisStudent.placement == comp:
        if request.method == 'POST':
            if 'save' in request.POST:
                form = ChangeSupervisorForm(request.POST, company=comp, instance=thisStudent)
                if form.is_valid():
                    thisStudent = form.save()
                    LogEntry.objects.log_action(
                        user_id         = request.user.pk,
                        content_type_id = ContentType.objects.get_for_model(thisStudent).pk,
                        object_id       = thisStudent.pk,
                        object_repr     = unicode(thisStudent),
                        action_flag     = CHANGE,
                        change_message  = "Changed supervisor to " + unicode(thisStudent.primary_contact)
                    )
                    return supervisor_dash(request, "Primary supervisor changed.")
                else:
                    return render_to_response('work_study/supervisor_change_primary.html', {'student': thisStudent, 'form': form, 'supervisor':True}, RequestContext(request, {}))
            elif 'edit' in request.POST:
                form = ChangeSupervisorForm(request.POST, company=comp, instance=thisStudent)
                if form.is_valid():
                    form = form.save(commit=False)
                    request.session['super'] = form.primary_contact
                    form = AddSupervisor(instance=form.primary_contact)
                    return render_to_response('work_study/supervisor_edit.html', {'company': comp, 'student': thisStudent, 'form': form, 'supervisor':True}, RequestContext(request, {}))
                else:
                    return render_to_response('work_study/supervisor_change_primary.html', {'student': thisStudent, 'form': form, 'supervisor':True}, RequestContext(request, {}))
            elif 'edit_complete' in request.POST:
                form = AddSupervisor(request.POST, instance=request.session['super'])
                del request.session['super']
                if form.is_valid():
                    cont = form.save()
                    thisStudent.prcreate_time_cardimary_contact = cont
                    thisStudent.save()
                    return supervisor_dash(request, "Primary supervisor saved.")
                else:
                    return render_to_response('work_study/supervisor_edit.html', {'company': comp, 'student': thisStudent, 'form': form, 'supervisor':True}, RequestContext(request, {}))
            elif 'add' in request.POST:
                form = AddSupervisor()
                return render_to_response('work_study/supervisor_add.html', {'company': comp, 'student': thisStudent, 'form': form, 'supervisor':True}, RequestContext(request, {}))
            # save data from adding supervisor
            elif 'add_complete' in request.POST:
                form = AddSupervisor(request.POST)
                if form.is_valid():
                    cont = form.save()
                    comp.contacts.add(cont)
                    comp.save()
                    thisStudent.primary_contact = cont
                    thisStudent.save()
                    LogEntry.objects.log_action(
                        user_id         = request.user.pk,
                        content_type_id = ContentType.objects.get_for_model(thisStudent).pk,
                        object_id       = thisStudent.pk,
                        object_repr     = unicode(thisStudent),
                        action_flag     = CHANGE,
                        change_message  = "Changed supervisor to " + unicode(thisStudent.primary_contact)
                    )
                    return supervisor_dash(request, "Primary supervisor added.")
                else:
                    return render_to_response('work_study/supervisor_add.html', {'company': comp, 'student': thisStudent, 'form': form, 'supervisor':True}, RequestContext(request, {}))
        else:
            form = ChangeSupervisorForm(company=comp, instance=thisStudent)
            return render_to_response('work_study/supervisor_change_primary.html', {'student': thisStudent, 'form': form, 'supervisor':True}, RequestContext(request, {}))
    else:
        return HttpResponse("Access Denied")

@user_passes_test(lambda u: u.has_perm('work_study.change_studentworker') or u.has_perm('sis.reports'))
def report_builder_view(request):
    try:
        active_year = SchoolYear.objects.get(active_year=True)
    except SchoolYear.DoesNotExist:
        messages.warning(request, 'No Active Year Set, please create an active year!')
        return HttpResponseRedirect('/')

    form = ReportBuilderForm(initial={'custom_billing_begin':active_year.start_date,'custom_billing_end':active_year.end_date})
    template_form = ReportTemplateForm()
    if request.method == 'POST':
        if 'attnMonday' in request.POST:
            return gen_attendance_report_day('M')
        elif 'attnTuesday' in request.POST:
            return gen_attendance_report_day('T')
        elif 'attnWednesday' in request.POST:
            return gen_attendance_report_day('W')
        elif 'attnThursday' in request.POST:
            return gen_attendance_report_day('TH')
        elif 'attnFriday' in request.POST:
            return gen_attendance_report_day('F')

        elif 'attnPMonday' in request.POST:
            return gen_attendance_report_day('M', is_pickup=True)
        elif 'attnPTuesday' in request.POST:
            return gen_attendance_report_day('T', is_pickup=True)
        elif 'attnPWednesday' in request.POST:
            return gen_attendance_report_day('W', is_pickup=True)
        elif 'attnPThursday' in request.POST:
            return gen_attendance_report_day('TH', is_pickup=True)
        elif 'attnPFriday' in request.POST:
            return gen_attendance_report_day('F', is_pickup=True)

        elif 'pod_report' in request.POST:
            template_form = ReportTemplateForm(request.POST, request.FILES)
            if template_form.is_valid():
                students = template_form.get_students(template_form.cleaned_data, worker=True)
                template = template_form.get_template(request)
                if template:
                    report = TemplateReport(request.user)
                    report.data['workteams'] = WorkTeam.objects.all()
                    report.data['students'] = students
                    report.filename = 'Work Study Report'
                    return report.pod_save(template)
        else:
            form = ReportBuilderForm(request.POST)
            if form.is_valid():
                # pre-made reports
                if 'fteInd' in request.POST:
                    return fte_by_ind(request)
                elif 'fteDay' in request.POST:
                    return fte_by_day(request)
                elif 'ftePay' in request.POST:
                    return fte_by_pay(request)
                elif 'history' in request.POST:
                    hist = CompanyHistory.objects.all()
                    data = []
                    for h in hist:
                        data.append([unicode(h.getStudent()), h.placement, h.date])
                    titles = (["Student", "WorkTeam left", "Date",])
                    report = XlReport(file_name="company_history")
                    report.add_sheet(data, header_row=titles, title="Company History", heading="Company History")
                    return report.as_download()
                elif 'dols' in request.POST:
                    return dol_xls_report(form.cleaned_data['custom_billing_begin'], form.cleaned_data['custom_billing_end'])
                elif 'contracts' in request.POST:
                    return contracts_report()
                elif 'attendance' in request.POST:
                    attend = Attendance.objects.filter(absence_date__range=(form.cleaned_data['custom_billing_begin'], form.cleaned_data['custom_billing_end'])).exclude(tardy="P")
                    # Sheet 1 all absences
                    data = []
                    titles = ["Date", "First Name", "Last", "Grade", "Total", "comments", "make up date", "Bill", "Was Billed?"]
                    for at in attend:
                        if at.half_day: half = "1/2"
                        else: half = "1"
                        if at.waive: makeup = "Waived"
                        else: makeup = at.makeup_date
                        if at.billed: billed = "Yes"
                        else: billed = "No"
                        data.append([at.absence_date, at.student.first_name, at.student.last_name, at.student.year, half, at.reason, makeup, at.fee, billed])

                    report = XlReport(file_name="attendance_report")
                    report.add_sheet(data, header_row=titles, title="Total")

                    # waived
                    waivers = attend.filter(waive=True)
                    data = []
                    titles = ["Date", "First Name", "Last", "WorkTeam", "Grade", "Total", "comments", "Bill"]
                    for at in waivers:
                        if at.half_day: half = "1/2"
                        else: half = "1"
                        data.append([at.absence_date, at.student.first_name, at.student.last_name, at.student.placement, at.student.year, half, at.reason, at.fee])
                    report.add_sheet(data, header_row=titles, title="Waived")

                    # pending meaning no makeup date and not waived
                    pend = attend.filter(makeup_date=None).filter(waive=None).order_by('billed')
                    data = []
                    titles = ["Date", "First Name", "Last", "WorkTeam", "Grade", "Total", "comments", "Workday", "Make up date", "Bill", "Was billed?"]
                    for at in pend:
                        if at.half_day: half = "1/2"
                        else: half = "1"
                        if at.waive: makeup = "Waived"
                        else: makeup = at.makeup_date
                        if at.billed: billed = "Yes"
                        else: billed = "No"
                        data.append([at.absence_date, at.student.first_name, at.student.last_name, at.student.placement, at.student.year, half, at.reason, at.student.get_day_display(), makeup, at.fee, billed])
                    report.add_sheet(data, header_row=titles, title="Pending")

                    # scheduled
                    sced = attend.filter(~Q(makeup_date=None)).filter(waive=None)
                    data = []
                    titles = ["Date", "First Name", "Last", "WorkTeam", "Supervisor", "Grade", "Total", "comments", "Make up date", "Bill"]
                    for at in sced:
                        if at.half_day: half = "1/2"
                        else: half = "1"
                        if at.waive: makeup = "Waived"
                        else: makeup = at.makeup_date
                        data.append([at.absence_date, at.student.first_name, at.student.last_name, at.student.placement, at.student.primary_contact, at.student.year, half, at.reason, makeup, at.fee])
                    report.add_sheet(data, header_row=titles, title="Scheduled")

                    # outstanding bills, sum of student's fee - paid
                    bills = attend.filter(billed=None)
                    summary = bills.values('student').annotate(Sum('fee__value'), Sum('paid')).values('student__first_name', 'student__last_name', 'fee__value__sum', 'paid__sum')
                    data = []
                    for at in summary:
                        if at['fee__value__sum'] or at['paid__sum']:
                            total_owes = 0
                            if at['fee__value__sum'] and at['paid__sum']:
                                total_owes = at['fee__value__sum'] - at['paid__sum']
                            data.append([at['student__first_name'], at['student__last_name'], at['fee__value__sum'], at['paid__sum'], total_owes])

                    titles = ["Fname", "Lname", "Total Fee", "Total Paid", "Total owes school (does not include students who were already billed)"]
                    report.add_sheet(data, header_row=titles, title="Bill Summary")

                    timesheets = TimeSheet.objects.filter(date__range=(form.cleaned_data['custom_billing_begin'], form.cleaned_data['custom_billing_end']))
                    data = []
                    titles = ["Date", "First Name", "Last", "Grade", "WorkTeam", "Hours", "School Net Pay", "Student Net Pay"]
                    for ts in timesheets:
                        data.append([ts.date, ts.student.first_name, ts.student.last_name, ts.student.year, ts.company, ts.hours, ts.school_net, ts.student_net])
                    report.add_sheet(data, header_row=titles, title="TimeSheets")
                    return report.as_download()

                # All students and the the number of timesheets submitted for some time period
                elif 'student_timesheet' in request.POST:
                    data = []
                    titles = ["Student", "Work Day", "Placement", "Number of work study Presents", "Number of time sheets submitted", "Dates"]
                    students = StudentWorker.objects.filter(is_active=True)
                    for student in students:
                        ts = TimeSheet.objects.filter(student=student).filter(date__range=(form.cleaned_data['custom_billing_begin'], form.cleaned_data['custom_billing_end']))
                        present_count = student.attendance_set.filter(absence_date__range=(form.cleaned_data['custom_billing_begin'], form.cleaned_data['custom_billing_end']), tardy="P").count()
                        dates = ""
                        for t in ts:
                            dates += unicode(t.date) + ", "
                        data.append([student, student.day, student.placement, present_count, ts.count(), dates])
                    report = XlReport(file_name="Student_timesheets")
                    report.add_sheet(data, header_row=titles, title="Student Timesheets")
                    return report.as_download()

                # billing report for time worked for own pay.
                elif 'billing' in request.POST:
                    timesheets = TimeSheet.objects.filter(Q(date__range=(form.cleaned_data['custom_billing_begin'], form.cleaned_data['custom_billing_end'])) & \
                        Q(for_pay__iexact=1) & Q(approved__iexact=1)).order_by('student', 'date')
                    data = []
                    titles = ["Company", "Work Team", "Student", "", "Date", "Hours Worked", "Student Salary", "Company Bill"]
                    companies = WorkTeam.objects.all()
                    total_hours = 0
                    total_student_salary = 0
                    total_company_bill = 0
                    for company in companies:
                        new_company = True
                        studenti = 0    # counter for # of days a student worked at a company.
                        for timesheet in timesheets:
                            if (timesheet.company == company):
                                if new_company:
                                    new_company = False
                                    company_total = timesheets.filter(company__id__iexact=company.id).aggregate(Sum('school_net'))
                                    data.append([company.company, company, "", "", "", "", "", ""])
                                data.append(["", "", timesheet.student.first_name, timesheet.student.last_name, timesheet.date, timesheet.hours, \
                                    timesheet.student_net, timesheet.school_net])
                                studenti += 1
                                # if last day for this student print out the student's totals
                                if studenti == timesheets.filter(company__id__iexact=company.id).filter(student__id__iexact=timesheet.student.id).count():
                                    stu_total = timesheets.filter(company__id__iexact=company.id).filter(student__id__iexact=timesheet.student.id). \
                                        aggregate(Sum('hours'), Sum('student_net'), Sum('school_net'))
                                    # guard against aggregates that are None
                                    for k, v in stu_total.iteritems():
                                        if v is None:
                                            stu_total[k] = 0
                                    data.append(["", "", "", "", "Total", stu_total['hours__sum'], stu_total['student_net__sum'], \
                                        stu_total['school_net__sum']])
                                    total_hours += stu_total['hours__sum']
                                    if stu_total['student_net__sum']:
                                        total_student_salary += stu_total['student_net__sum']
                                    total_company_bill += stu_total['school_net__sum']
                                    studenti = 0
                        # if we did add a company, now the days are entered lets aggregate
                        if not new_company:
                            company_total = timesheets.filter(company__id__iexact=company.id).aggregate(Sum('school_net'))
                            data.append(["Company Total:", "", "", "", "", "", "", company_total['school_net__sum']])
                            data.append(["",])
                    data.append(["",])
                    data.append(["Totals:", "", "", "", "", total_hours, total_student_salary, total_company_bill])
                    report = XlReport(file_name="Billing_Report")
                    report.add_sheet(data, header_row=titles, title="Detailed Hours")

                    ### WorkTeam Summary
                    data = []
                    comp_totals = timesheets.values('company').annotate(Count('student', distinct=True), Sum('hours'), Avg('hours'), Sum('student_net'), \
                            Sum('school_net')).values('company', 'company__company__name', 'company__team_name', 'student__count', 'hours__sum', 'hours__avg', 'student_net__sum', 'school_net__sum')
                    for c in comp_totals.order_by('company__company'):
                        data.append([c['company__company__name'], c['company__team_name'], c['student__count'], c['hours__sum'], c['hours__avg'], c['student_net__sum'], c['school_net__sum']])
                    titles = ["Company", "WorkTeam", "Workers Hired", "Hours Worked", "Avg Hours per Student", "Gross Amount Paid to Students", "Amount Billed to Company"]
                    report.add_sheet(data, header_row=titles, title="Work Team Summary")

                    ### Company Summary
                    data = []
                    comp_totals = timesheets.values('company__company__id').annotate(Count('student', distinct=True), Sum('hours'), Avg('hours'), Sum('student_net'), \
                            Sum('school_net')).values('company__company__name', 'student__count', 'hours__sum', 'hours__avg', 'student_net__sum', 'school_net__sum').order_by('company__company')

                    for c in comp_totals:
                        data.append([c['company__company__name'], c['student__count'], c['hours__sum'], c['hours__avg'], c['student_net__sum'], c['school_net__sum']])
                    titles = ["Company", "Workers Hired", "Hours Worked", "Avg Hours per Student", "Gross Amount Paid to Students", "Amount Billed to Company"]
                    report.add_sheet(data, header_row=titles, title="Company Summary")

                    ### Payroll (ADP #s)
                    data = []
                    students = StudentWorker.objects.filter(timesheet__in=timesheets)
                    for student in students:
                        ts = timesheets.filter(student=student).aggregate(Sum('hours'), Sum('student_net'))
                        data.append([student.unique_id, student.first_name, student.last_name, student.adp_number, ts['hours__sum'], ts['student_net__sum']])
                    titles = ['Unique ID', 'First Name', 'Last Name', 'ADP #', 'Hours Worked', 'Gross Pay']
                    report.add_sheet(data, header_row=titles, title="Payroll (ADP #s)")

                    ### Student info wo ADP#
                    data = []
                    for student in students:
                        if not student.adp_number:
                            ts = timesheets.filter(student=student).aggregate(Sum('student_net'))
                            data.append([student.last_name, student.first_name, student.parent_guardian, student.street, \
                                student.city, student.state, student.zip, student.ssn, ts['student_net__sum']])
                    titles = ['lname', 'fname', 'parent', 'address', 'city', 'state', 'zip', 'ss', 'pay']
                    report.add_sheet(data, header_row=titles, title="Student info wo ADP #")

                    return report.as_download()

                elif 'all_timesheets' in request.POST:
                    timesheets = TimeSheet.objects.filter(date__range=(form.cleaned_data['custom_billing_begin'], form.cleaned_data['custom_billing_end'])).order_by('student', 'date')
                    data = []
                    titles = ["Name", "", "For Pay", "make up", "approved", "company",
                              "creation date", "date", "Time In", "Lunch", "Lunch Return", "Out", "Hours",
                              "Student net", "School net", "Student Accomplishment", "Performance", "Supervisor Comment"]
                    for ts in timesheets:
                        data.append([ts.student.first_name, ts.student.last_name, ts.for_pay, ts.make_up,
                                     ts.approved, ts.company, ts.creation_date, ts.date, ts.time_in,
                                     ts.time_lunch, ts.time_lunch_return, ts.time_out, ts.hours,
                                     ts.student_net, ts.school_net, ts.student_accomplishment,
                                     ts.performance, ts.supervisor_comment])
                    report = XlReport(file_name="timesheets")
                    report.add_sheet(data, header_row=titles, title="timesheets")
                    return report.as_download()

                # master contact list
                elif 'master' in request.POST:
                    workers = (StudentWorker.objects.all()).exclude(is_active=False)
                    data = []
                    for worker in workers:
                        eFname = eLname = eHome = eWork = eCell = ""
                        number = worker.get_phone_number()
                        if worker.emergency_contacts.filter(primary_contact=True):
                            primary_ec = worker.emergency_contacts.filter(primary_contact=True)[0]
                            eFname = primary_ec.fname
                            eLname = primary_ec.lname
                            if primary_ec.emergencycontactnumber_set.filter(type="H"):
                                eHome = primary_ec.emergencycontactnumber_set.filter(type="H")[0].number
                            if primary_ec.emergencycontactnumber_set.filter(type="W"):
                                eWork = primary_ec.emergencycontactnumber_set.filter(type="W")[0].number
                            if primary_ec.emergencycontactnumber_set.filter(type="C"):
                                eCell = primary_ec.emergencycontactnumber_set.filter(type="C")[0].number

                        if worker.primary_contact:
                            supFname = worker.primary_contact.fname
                            supLname = worker.primary_contact.lname
                            supPhone = worker.primary_contact.phone
                            supCell = worker.primary_contact.phone_cell
                            supEmail = worker.primary_contact.email
                        else:
                            supFname = "No supervisor assigned"
                            supLname = "No supervisor assigned"
                            supPhone = " "
                            supCell = " "
                            supEmail =" "

                        data.append([worker.first_name, worker.last_name, worker.mname, worker.year, worker.day, supFname,\
                            supLname,supPhone, supCell,supEmail,number,eFname,eLname,eHome,eCell,eWork])
                    titles = ['First Name', 'Last Name', 'Middle Name','Year', 'Work Day', 'Supervisor First Name', 'Supervisor Last Name', 'Supervisor Phone', \
                        'Supervisor Cell', 'Supervisor Email', 'Student Cell', 'Parent First Name', 'Parent Last Name', 'Parent Home', 'Parent Cell', 'Parent Work']
                    report = XlReport(file_name="StudentMasterContactList")
                    report.add_sheet(data, header_row=titles, title="Custom Report")
                    return report.as_download()
            else:
                return render_to_response('work_study/reportBuilder.html', {'form': form,'request':request, 'template_form': template_form}, RequestContext(request, {}))
    return render_to_response('work_study/reportBuilder.html', {'form': form,'request':request, 'template_form': template_form}, RequestContext(request, {}))


@permission_required('discipline.change_clientvisit')
def dol_form(request, id=None):
    supervisors_text = ""
    if id:
        for supervisor in ClientVisit.objects.get(id=id).supervisor.all():
            supervisors_text += unicode(supervisor) + ", "
    supervisors_text = supervisors_text[:-2]
    if request.method == 'POST':
        if id:
            form = DolForm(request.POST, instance=ClientVisit.objects.get(id=id))
            form.save(commit=False)
        else:
            form = DolForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'DOL client visit saved')
            if '_addanother' in request.POST:
                form = DolForm()
                return render_to_response('work_study/DOL.html', {'form': form,'request':request, 'messages': messages.get_messages(request)}, RequestContext(request, {}))
            else:
                return HttpResponseRedirect('/admin/work_study/clientvisit')
        else:
            return render_to_response('work_study/DOL.html', {'form': form,'request':request}, RequestContext(request, {}))
    else:
        if id:
            clientvisit = ClientVisit.objects.get(id=id)
            form = DolForm(instance=clientvisit)
        else:
            form = DolForm()
        return render_to_response('work_study/DOL.html', {'form': form, 'supervisors':supervisors_text, 'request':request}, RequestContext(request, {}))

def dol_xls_report(begin_date, end_date,):
    data = []
    titles = ["Work Team", "CRA", "Total visits", "DOL visits (in specified dates)", "Visit in active year?", "Last visited"]

    teams = WorkTeam.objects.all().annotate(Count('clientvisit'))
    for team in teams:
        if team.is_active():
            dol_last = None
            dols = ClientVisit.objects.filter(company=team, dol=True).order_by('-date')
            if begin_date and end_date:
                dols = dols.filter(date__range=(begin_date, end_date))
            if dols.count() > 0:
                if dols[0].date > SchoolYear.objects.get(active_year=True).start_date:
                    dol_this_year = "Yes"
                else:
                    dol_this_year = "No"
                dol_last = unicode(dols[0].date)
            else:
                dol_this_year = "No"
            data.append([team.team_name, team.cra, team.clientvisit__count, dols.count(), dol_this_year, dol_last])

    report = XlReport(file_name="Client_visit_report")
    report.add_sheet(data, header_row=titles, title="Client Visit Report")
    return report.as_download()

@user_passes_test(lambda u: u.has_perm('work_study.change_studentinteraction') or u.has_perm('sis.reports'))
def student_meeting(request):
    try:
        start_date = SchoolYear.objects.get(active_year=True).start_date
    except: start_date = None
    meetings = []

    for student in StudentWorker.objects.filter(is_active=True):
        meeting = struct()
        meeting.student = student
        interactions = StudentInteraction.objects.filter(type="M", student=student).order_by('-date')
        if interactions.count() > 0:
            meeting.date = interactions[0].date
            try:
                if interactions[0].date > start_date:
                    meeting.met = "Yes"
                else:
                    meeting.met = "No"
            except:
                meeting.met = "Error"

        meetings.append(meeting)
    return render_to_response('work_study/student_meeting.html', {'request': request, 'meetings': meetings}, RequestContext(request, {}))

def company_contract1(request, id):
    company = get_object_or_404(Company, pk=id)

    if request.method == 'POST':
        form = CompanyContactForm1(request.POST)
        if form.is_valid():
            contract = form.save()
            return HttpResponseRedirect('/work_study/company_contract2/%s/' % contract.id)
    else:
        form = CompanyContactForm1(initial={'company':company})
    return render_to_response('work_study/company_contract1.html', {'request': request, 'form':form, 'company':company}, RequestContext(request, {}))

def company_contract2(request, id):
    contract = CompContract.objects.get(id=id)
    company = contract.company
    payment_options = PaymentOption.objects.all()

    for option in payment_options:
        option.cost = option.get_cost(contract.number_students)

    if request.method == 'POST':
        form = CompanyContactForm2(request.POST, instance=contract)
        if form.is_valid():
            contract = form.save()
            contract.generate_contract_file()
            return HttpResponseRedirect('/work_study/company_contract3/%s/' % contract.id)
    else:
        form = CompanyContactForm2()
    return render_to_response('work_study/company_contract2.html', {'request': request, 'form':form, 'company':company, 'payment_options':payment_options}, RequestContext(request, {}))

def company_contract3(request, id):
    contract = CompContract.objects.get(id=id)
    company = contract.company
    contact_info = Configuration.objects.get_or_create(name="Work Study Contract Number")[0].value

    if request.method == 'POST':
        form = CompanyContactForm3(request.POST)
        if form.is_valid():
            contract.signed = True
            contract.name = form.cleaned_data['name']
            contract.ip_address = request.META['REMOTE_ADDR']
            contract.save()
            contract.generate_contract_file()
            return HttpResponseRedirect('/work_study/company_contract_complete/%s?email=%s' % (contract.id,form.cleaned_data['email']))
    else:
        form = CompanyContactForm3(instance=contract)
    return render_to_response('work_study/company_contract3.html', {
        'request': request,
        'form':form,
        'contact_info': contact_info,
        'company':company,
        'contract':contract,
    }, RequestContext(request, {}))

def company_contract_complete(request, id):
    contract = CompContract.objects.get(id=id)
    company = contract.company
    email = request.GET.get('email')
    if email:
        try:
            message = Configuration.get_or_default(
                name="work_study_contract_complete_email_message",
                default='Thank you for agreeing to hire Cristo Rey students.',
            ).value
            mail = EmailMessage(
                'Work Study Contract Confirmation for %s.' % (company,),
                message,
                Configuration.get_or_default("work_study_contract_from_address", "donotreply@cristoreyny.org").value,
                [email],
            )

            cc = Configuration.get_or_default("work_study_contract_cc_address", "").value
            if cc:
                mail.cc = cc.split(',')
            attach = contract.get_contract_as_pdf(response=False)
            mail.attach('contract.pdf', attach.read(), 'application/pdf')
            mail.send()
        except:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(
                'Could not send email for a contract',
                exc_info=True,
                extra={'request': request,'exception':exc_type,'traceback':'%s %s' % (fname,exc_tb.tb_lineno)}
            )

    return render_to_response('work_study/company_contract_complete.html', {'request': request, 'company':company, 'contract':contract}, RequestContext(request, {}))

def company_contract_pdf(request, id):
    contract = CompContract.objects.get(id=id)

     # Check if using IE
    if re.search('MSIE', request.META['HTTP_USER_AGENT']):
        return contract.get_contract_as_pdf(ie=True)
    else:
        return contract.get_contract_as_pdf()


def fte_chart(request):
    workteams = WorkTeam.objects.filter(inactive=False,studentworker__isnull=False).exclude(industry_type="").annotate(no_students=Count('studentworker')).order_by('industry_type','company__name')
    fte_chart = {}
    fte_per_student = Configuration.get_or_default(name="Students per FTE",default=".2").value
    for workteam in workteams:
        ftes = fte_chart.get(workteam.industry_type, 0.0)
        fte_chart[workteam.industry_type] = ftes + (workteam.no_students / float(fte_per_student))

    # Now order it
    import operator
    fte_chart = sorted(fte_chart.iteritems(), key=operator.itemgetter(1))
    fte_chart.reverse()

    # need the row to create anchors for a clickable chart
    row_index = {}
    i = 0
    for industry, fte in fte_chart:
        row_index[industry] = i
        i += 1

    workteams_by_industry = []
    workteams_in_industry = None
    last_industry = None
    for workteam in workteams:
        if workteam.industry_type != last_industry:
            if workteams_in_industry:
                workteams_by_industry.append([last_industry, workteams_in_industry, row_index[last_industry]])
            last_industry = workteam.industry_type
            workteams_in_industry = []
        if workteam.company not in workteams_in_industry:
            workteams_in_industry += [workteam.company]


    return render_to_response(
        'work_study/fte_chart.html',
        {'request': request,'fte_chart': fte_chart, 'workteams_by_industry':workteams_by_industry,'embed': 'embed' in request.GET},
        RequestContext(request, {}))

@user_passes_test(lambda u: u.has_perm('sis.reports'))
def routes(request):
    """ Route reports form for Notre Dame Cristo Rey
    """
    if request.POST:
        if 'am_route_attendance' or 'pm_route_attendance' in request.POST:
            return am_route_attendance(request)
    return render_to_response('work_study/routes.html', {'request': request}, RequestContext(request, {}))

@permission_required('work_study.change_attendance')
def take_attendance(request, work_day=None):
    today = date.today()
    if work_day:
        work_day = StudentWorker.dayOfWeek[int(work_day)][0]
    else:
        try:
            work_day = StudentWorker.dayOfWeek[today.weekday()][0]
        except IndexError:
            work_day = StudentWorker.dayOfWeek[0][0]
    students = StudentWorker.objects.filter(day=work_day, is_active=True)
    extra = students.count() - students.filter(attendance__absence_date=today).count()
    AttendanceFormSet = modelformset_factory(Attendance, form=QuickAttendanceForm, extra=extra)

    if request.POST:
        formset = AttendanceFormSet(request.POST)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Saved {0} attendance records'.format(students.count()))
            return HttpResponseRedirect(urlresolvers.reverse('admin:work_study_attendance_changelist'))
    else:
        existing_attendance = Attendance.objects.filter(absence_date=today)
        initial_data = []
        for student in students.exclude(attendance__absence_date=today):
            initial_data += [{'student': student}]
        formset = AttendanceFormSet(queryset=existing_attendance,initial=initial_data)
    i = 0

    return render_to_response(
        'work_study/take_attendance.html',
        {'request': request, 'work_day': work_day, 'formset': formset, 'date': today},
        RequestContext(request, {}))
