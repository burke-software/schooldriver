#       views.py
#       
#       Copyright 2011 Burke Software and Consulting LLC
#        Author David M Burke <david@burkesoftware.com>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

from django.shortcuts import render_to_response, get_object_or_404
from django.template import Context, loader
from django.conf.urls.defaults import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.db import connection
from django.http import HttpResponse
from django import forms
from django.core import serializers
from django.core.mail import mail_admins
from django.core.urlresolvers import reverse
from django.db.models import Sum, Count, Avg
from django import forms
from django.forms.models import modelformset_factory
from django.http import HttpResponseRedirect

from ecwsp.work_study.models import *
from ecwsp.administration.models import Configuration, AccessLog, Template
from ecwsp.work_study.forms import *
from ecwsp.work_study.xlsReport import *
from ecwsp.sis.models import *
from ecwsp.sis.report import *

from itertools import *
import csv
import copy
from datetime import date
from datetime import datetime
import xlwt as pycel
import random
import sys
import re

days = (["Monday", "M"],["Tuesday","T"],["Wednesday","W"],["Thursday","TH"],["Friday", "F"])
class struct(object): pass

def fte_by_ind(request):
    fileName = "report_fteByInd.xls"
    cursor = connection.cursor()
    fte = int(Configuration.get_or_default(name="Students per FTE"[0], default=5).value)
    cursor.execute("select industry_type, count(*)/" + str(fte) + " from work_study_studentworker left join work_study_workteam on work_study_workteam.id = "+\
        "work_study_studentworker.placement_id group by industry_type;")
    names = cursor.fetchall()
    titles = (["Industry", "FTE"])
    report = xlsReport(names, titles, fileName, heading="FTE by Industry Type")
    report.addSheet(student_company_day_report(industry_type=True), heading="Detail")
    return report.finish()

def fte_by_day(request):
    fileName = "report_fteByDay.xls"
    cursor = connection.cursor()
    fte = int(Configuration.get_or_default(name="Students per FTE"[0], default=5).value)
    cursor.execute("select day, count(*)/" + str(fte) + " from work_study_studentworker left join work_study_workteam on work_study_workteam.id = "+\
        "work_study_studentworker.placement_id group by day;")
    names = cursor.fetchall()
    titles = (["Day", "FTE"])
    report = xlsReport(names, titles, fileName, heading="FTE by Day of Week")
    report.addSheet(student_company_day_report(), heading="Detail")
    return report.finish()
    
def student_company_day_report(industry_type=False, paying=False):
    data = []
    data.append(['', '', 'Students Assigned'])
    data.append(['Work Team', '', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])
    if industry_type: order = 'industry_type'
    elif paying: order = 'paying'
    else: order = 'team_name'
    for team in WorkTeam.objects.all().order_by(order):
        if team.studentworker_set.all().count():
            if industry_type:
                row = [team, team.industry_type]
            elif paying:
                row = [team, team.get_paying_display()]
            else:
                row = [team, ""]
            for day in StudentWorker.dayOfWeek:
                students = team.studentworker_set.filter(day=day[0])
                txt = ""
                for student in students:
                    txt += unicode(student) + " "
                row.append(txt)
            data.append(row)
    return data

#@login_required
#def attendance(request):
#    pickups = PickupLocation.objects.all()
#    for pickup in pickups:
#        gen_attendance_report(str(pickup))
#    for day in days:
#        gen_attendance_report_day(day)
#    return render_to_response('work_study/attendance.html', {'pickup': pickups, 'days': tuple(x[0] for x in days)})
    
# Generate attendance by day    
def gen_attendance_report_day(day, is_pickup=False):
    """
    Generates a spreadsheet for a student worker based on their pickup or dropoff location.
    day: day of week
    is_pickup: Is this a pickup? If false it's a dropoff
    """
    wb = pycel.Workbook()
    
    # convert to stupid way to storing days.
    # 'F' -> ['Friday', 'F']
    for d in days:
        if d[1] == day:
            day = d
            break
    
    pickups = PickupLocation.objects.all()
    for pickup in pickups:
        ws = wb.add_sheet(pickup.location)
        ws.portrait = False
        
        myFont = pycel.Font()
        myFont.bold = True
        myFont.size = 18
        myFontStyle = pycel.XFStyle()
        myFontStyle.borders.bottom = 0x02
        myFontStyle.alignment.wrap = pycel.Alignment.WRAP_AT_RIGHT
        myFontStyle.font = myFont
        
        ws.col(0).width = 0x0a00
        ws.col(1).width = 0x0d00 + 1000
        ws.col(2).width = 0x0d00 + 2000
        ws.col(3).width = 0x0700 - 50
        ws.col(4).width = 0x0d00 + 1000
        ws.col(5).width = 0x0d00 + 20
        ws.col(6).width = 0x0d00 + 80
        ws.write(0,0,pickup.long_name)
        
        ws.write(0,2,"DATE:")
        ws.write(0,4,day[0])
        ws.write(1,0,"L=Late\nA=Absent\nX=Present  ")
        ws.write(1,1,"Student Name", myFontStyle)
        ws.write(1,2,"Company Name", myFontStyle)
        ws.write(1,3,"Train Line", myFontStyle)
        ws.write(1,4,"Stop Location", myFontStyle)
        ws.write(1,5,"Client", myFontStyle)
        ws.write(1,6,"Dress Code", myFontStyle)
        ws.write(1,7,"Phone Number", myFontStyle)
        
        myFontStyle = pycel.XFStyle()
        myFontStyle.alignment.wrap = pycel.Alignment.WRAP_AT_RIGHT
        myFontStyle.borders.left   = 0x01
        myFontStyle.borders.right  = 0x01
        myFontStyle.borders.top    = 0x01
        myFontStyle.borders.bottom = 0x01
        
        y=2
        if is_pickup == True:
            students = StudentWorker.objects.filter(day=day[1], placement__pickup_location__location=pickup).filter(inactive=False)
        else:
            students = StudentWorker.objects.filter(day=day[1], placement__dropoff_location__location=pickup).filter(inactive=False)
        for stu in students:
            if stu.fax:
                ws.write(y,0,"txt", myFontStyle)                            #Small font fax.
            else:
                ws.write(y,0," ", myFontStyle)                                #blank for absent/late
            ws.write(y,1,unicode(stu.fname + " " +stu.lname), myFontStyle)    #name
            ws.write(y,2,unicode(stu.placement), myFontStyle)                #placement
            ws.write(y,3,unicode(stu.placement.train_line), myFontStyle)    #train line
            ws.write(y,4,unicode(stu.placement.stop_location), myFontStyle)    #stop Location
            ws.write(y,5,unicode(stu.placement.cra), myFontStyle)            #CRA
            ws.write(y,6," ", myFontStyle)                                    #blank for dress code
            try:
                number = stu.studentnumber_set.filter(type="C")[0]
            except:
                number = None
            ws.write(y,7,unicode(number), myFontStyle)  
            y += 1
        
    response = HttpResponse(mimetype="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=%s' % ('Attendance_' + day[0] + '.xls' ,)
    wb.save(response)
    return response

def fte_by_pay(request):
    fileName = "report_fteByPay.xls"
    xls = customXls(fileName) 
    student_fte = int(Configuration.get_or_default(name="Students per FTE"[0], default=5).value)
    
    cursor = connection.cursor()
    cursor.execute("select paying, count(*)/" + str(student_fte) + " from work_study_studentworker left join work_study_workteam on work_study_workteam.id = "+\
        "work_study_studentworker.placement_id group by paying;")
    totals = cursor.fetchall()
    
    cursor = connection.cursor()
    cursor.execute("select team_name, paying, count(*)/" + str(student_fte) + ", funded_by as fte from work_study_studentworker left join work_study_workteam on "+\
        "work_study_workteam.id = work_study_studentworker.placement_id group by team_name order by paying, team_name;")
    company = cursor.fetchall()

    titles = (["Paying?","FTE"])
    xls.addSheet(totals, titles, "Totals")
    titles = (["WorkTeam", "Paying?","FTE", "Funded by"])
    xls.addSheet(company, titles, "Companies")
    xls.addSheet(student_company_day_report(paying=True), heading="Detail")
    return xls.finish()

class UploadFileForm(forms.Form):
    file  = forms.FileField()
    
class UploadSurveyForm(forms.Form):
    survey_name = forms.CharField(max_length=255, required=True)
    file  = forms.FileField()


@user_passes_test(lambda u: u.groups.filter(name='cwsp').count() > 0 or u.is_superuser == True, login_url='/')    
def import_student(request):
    form_survey = UploadSurveyForm()
    return render_to_response('work_study/upload.html', {'form_survey': form_survey, 'request': request,}, RequestContext(request, {}))

@user_passes_test(lambda u: u.groups.filter(name='faculty').count() > 0 or u.is_superuser, login_url='/')
def import_survey(request):
    if request.POST:
        form = UploadSurveyForm(request.POST, request.FILES)
        if form.is_valid():
            msg = []
            ex = []
            csvfile = request.FILES['file']
            csvfile.read()
            testReader = csv.reader(csvfile,delimiter=',', quotechar='"')
            header = testReader.next()
            i = 0
            for row in testReader:
                try:
                    # items will looks like
                    # [('student ID', '1'), ('Is student awesome?', 'Yes')]
                    items = zip(header, row)
                    student = StudentWorker.objects.get(id=items[0][1])
                    for item in items:
                        if item[0] != "student ID":
                            survey = Survey(survey=form.cleaned_data['survey_name'])
                            survey.student = student
                            survey.question = item[0]
                            survey.answer = item[1]
                            survey.save()
                            i += 1
                except:
                    print >> sys.stderr, "error"
            return render_to_response('upload.html', {'msg': "Success! " + str(i) + " entries made.", 'request': request,}, RequestContext(request, {}))
        else:
            return render_to_response('upload.html', {'form_survey': form,'request': request,}, RequestContext(request, {}))
    else:
        return import_student(request)

def import_number(value):
    phonePattern = re.compile(r'''
                # don't match beginning of string, number can start anywhere
    (\d{3})     # area code is 3 digits (e.g. '800')
    \D*         # optional separator is any number of non-digits
    (\d{3})     # trunk is 3 digits (e.g. '555')
    \D*         # optional separator
    (\d{4})     # rest of number is 4 digits (e.g. '1212')
    \D*         # optional separator
    (\d*)       # extension is optional and can be any number of digits
    $           # end of string
    ''', re.VERBOSE)
    a, b, c, ext = phonePattern.search(value).groups()
    if ext == "0000":
        ext = ""
    return a + "-" + b + "-" + c, ext

@user_passes_test(lambda u: u.groups.filter(name='students').count() > 0 or u.is_superuser, login_url='/')
def student_timesheet(request):
    """ A student's timesheet. """
    try:
        thisStudent = StudentWorker.objects.get(username=request.user.username)
        compContacts = Contact.objects.filter(workteam=thisStudent.placement)
    except:
        return render_to_response('base.html', {'msg': "Student or Company does not exist. Please notify a system admin if you believe this is a mistake."}, RequestContext(request, {}))
    try:
        supervisorName = thisStudent.primary_contact.fname + " " + thisStudent.primary_contact.lname
    except:
        supervisorName = "No Supervisor"
    if request.method == 'POST':
        form = TimeSheetForm(request.POST)
        # check to make sure hidden field POST data isn't tampered with
        if form.is_valid() and (request.POST['company'] == str(thisStudent.placement.id)) and (request.POST['student'] == str(thisStudent.id)):
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
            form.save()
            access = AccessLog()
            access.login = request.user
            access.ua = request.META['HTTP_USER_AGENT']
            access.ip = request.META['REMOTE_ADDR']
            access.usage = "Student submitted time sheet"
            access.save()
            return render_to_response('base.html', {'student': True, 'msg': "Timesheet has be successfully submitted, your supervisor has been notified."}, RequestContext(request, {}))
        else:
            pay, created = Configuration.objects.get_or_create(name="Allow for pay")
            if created: 
                pay.value = "True"
                pay.save()
            if pay.value != "True" and pay.value != "true": form.fields['for_pay'].widget = forms.HiddenInput()
            return render_to_response('work_study/student_timesheet.html', {'student': True, 'form': form, 
                'studentName': thisStudent, 'supervisorName': supervisorName,}, RequestContext(request, {}))
    else:
        try:
            if thisStudent.primary_contact: initial_primary = thisStudent.primary_contact.id
            else: initial_primary = None
            form = TimeSheetForm(initial={'student':thisStudent.id, 'company':thisStudent.placement.id, 'my_supervisor':initial_primary,
                'date': date.today, 'time_in': "9:30 AM", 'time_lunch': "12:00 PM", 'time_lunch_return': "1:00 PM", 'time_out': "5:00 PM"})
            form.set_supers(compContacts)
        except:
            return render_to_response('base.html', {'msg': "Student or Company does not exist. Please notify a system admin if you believe this is a mistake."}, RequestContext(request, {}))
        # Should for_pay be an option?
        pay, created = Configuration.objects.get_or_create(name="Allow for pay")
        if created: 
            pay.value = "True"
            pay.save()
        if pay.value != "True" and pay.value != "true": form.fields['for_pay'].widget = forms.HiddenInput()
        
        return render_to_response('work_study/student_timesheet.html', {'student': True, 'form': form, 'studentName': thisStudent, \
            'supervisorName': supervisorName,}, RequestContext(request, {}))

def timesheet_delete(request):
    # first check if key is valid, this replaces the need for login.
    key = request.GET.get('key', '')
    try:
        sheet = TimeSheet.objects.get(supervisor_key = key)
    except:
        return render_to_response('base.html', {'supervisor': True,'msg': "Link not valid. Was this timesheet already approved?"}, RequestContext(request, {}))
    sheet.delete()
    return supervisor_dash(request, "Deleted time card")
        
def approve(request):
    # first check if key is valid, this replaces the need for login.
    key = request.GET.get('key', '')
    try:
        sheet = TimeSheet.objects.get(supervisor_key = key)
    except:
        return render_to_response('base.html', {'supervisor': True,'msg': "Link not valid. Was this timesheet already approved?"}, RequestContext(request, {}))
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
            if sheet.show_student_comments:
                sheet.emailStudent()
            else:
                sheet.emailStudent(show_comment=False)
            return render_to_response('base.html', {'supervisor': True,'msg':"Time Card Approved!"}, RequestContext(request, {}))
        else:
            compContacts = Contact.objects.filter(workteam=sheet.student.placement)
            form.set_supers(compContacts)
            return render_to_response('work_study/student_timesheet.html', {'supervisor': True,'approved': sheet.approved, 'form': form, \
                'studentName': sheet.student, 'supervisorName': sheet.student.primary_contact,}, RequestContext(request, {}))
    else:
        if sheet.student.primary_contact: initial_primary = sheet.student.primary_contact.id
        else: initial_primary = None
        form = TimeSheetForm(instance=sheet, initial={'edit':True, 'my_supervisor':initial_primary,})
        compContacts = Contact.objects.filter(workteam=sheet.student.placement)
        form.set_supers(compContacts)
        return render_to_response('work_study/student_timesheet.html', {'supervisor': True, 'approved': sheet.approved, 'form': form, \
            'studentName': sheet.student, 'supervisorName': sheet.student.primary_contact,}, RequestContext(request, {}))
    

@user_passes_test(lambda u: u.groups.filter(name='company').count() > 0 or u.is_superuser, login_url='/')
def supervisor_dash(request, msg=""):
    comp = WorkTeam.objects.filter(login=request.user)[0]
    if 'mass_approve' in request.POST:
        msg="All checked time sheets approved"
        timeSheets = TimeSheet.objects.filter(company=comp).filter(approved=False)
        # for each post value
        for check in request.POST.values():
            # is it an id in the timesheet? Only check this companies timesheets
            for ts in timeSheets:
                if str(ts.id) == str(check):
                    ts.approved = True
                    ts.save()
    students = StudentWorker.objects.filter(placement=comp)
    timeSheets = TimeSheet.objects.filter(company=comp).filter(approved=False)
    TimeSheetFormSet = modelformset_factory(TimeSheet, fields=('approved',))
    timeSheetsApprovedForm = TimeSheetFormSet(queryset=timeSheets)
    try:
        access = AccessLog()
        access.login = request.user
        access.ua = request.META['HTTP_USER_AGENT']
        access.ip = request.META['REMOTE_ADDR']
        access.usage = "Supervisor Dash"
        access.save()
    except:
        print >> sys.stderr, "error creating access log"
    return render_to_response('work_study/supervisor_dash.html', {'supervisor': True,'msg': msg, 'comp': comp, 'students': students, \
        'timeSheets': timeSheets, 'timeSheetsApprovedForm': timeSheetsApprovedForm}, RequestContext(request, {}))

@user_passes_test(lambda u: u.groups.filter(name='company').count() > 0 or u.is_superuser, login_url='/')
def supervisor_xls(request):
    comp = WorkTeam.objects.filter(login=request.user)[0]
    timesheets = TimeSheet.objects.filter(approved=True).filter(company=comp).order_by('student', 'date',)
    data = []
    titles = ["WorkTeam", "Student", "", "Date", "For Pay?", "Make up?", "Hours Worked", "Company Bill"]
    fileName = "Billing_Report.xls"
    company_total = timesheets.aggregate(Sum('school_net'))
    data.append([comp.team_name, "", "", "", "", "", "", company_total['school_net__sum']])
    studenti = 0
    for timesheet in timesheets:
        data.append(["", timesheet.student.fname, timesheet.student.lname, timesheet.date, timesheet.for_pay, timesheet.make_up, timesheet.hours, timesheet.school_net])
        studenti += 1
        if studenti == timesheets.filter(student__id__iexact=timesheet.student.id).count():
            stu_total = timesheets.filter(student__id__iexact=timesheet.student.id).aggregate(Sum('hours'), Sum('student_net'), Sum('school_net'))
            data.append(["", "", "", "Total", "", "", stu_total['hours__sum'], stu_total['school_net__sum']])
            studenti = 0
    report = xlsReport(data, titles, fileName, heading="Company Billing")
    
    return report.finish()
        
@user_passes_test(lambda u: u.groups.filter(name='company').count() > 0 or u.is_superuser, login_url='/')
def supervisor_view(request):
    comp = WorkTeam.objects.filter(login=request.user)[0]
    students = StudentWorker.objects.filter(placement=comp)
    timeSheets = TimeSheet.objects.filter(company=comp).filter(approved=True).order_by('date').reverse()[:100]
    return render_to_response('work_study/supervisor_view.html', {'supervisor': True, 'timeSheets': timeSheets}, RequestContext(request, {}))
    
@user_passes_test(lambda u: u.groups.filter(name='students').count() > 0 or u.is_superuser, login_url='/')
def student_view(request):
    thisStudent = StudentWorker.objects.get(username=request.user.username)
    timeSheets = TimeSheet.objects.filter(student=thisStudent).order_by('date').reverse()[:100]
    return render_to_response('work_study/student_view.html', {'timeSheets': timeSheets, 'student': thisStudent}, RequestContext(request, {}))
    
@user_passes_test(lambda u: u.groups.filter(name='students').count() > 0 or u.is_superuser, login_url='/')
def student_edit(request, tsid):
    """ Student edits own timesheet """
    thisStudent = StudentWorker.objects.get(username=request.user.username)
    timesheet = TimeSheet.objects.get(id=tsid)
    if (timesheet.student != thisStudent): raise Exception('PermissionDenied',)
    compContacts = Contact.objects.filter(workteam=thisStudent.placement)
    try:
        supervisorName = thisStudent.primary_contact.fname + " " + thisStudent.primary_contact.lname
    except:
        supervisorName = "No Supervisor"
    if request.method == 'POST':
        form = TimeSheetForm(request.POST, request.FILES, instance=timesheet)
        # check to make sure hidden field POST data isn't tampered with
        if form.is_valid() and (request.POST['company'] == str(thisStudent.placement.id)) and (request.POST['student'] == str(thisStudent.id)):
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
            form.save()
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

@user_passes_test(lambda u: u.groups.filter(name='company').count() > 0 or u.is_superuser, login_url='/')    
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
                if sheet.show_student_comments:
                    sheet.emailStudent()
                else:
                    sheet.emailStudent(show_comment=False)
                return supervisor_dash(request, "Timesheet submitted for " + thisStudent.fname)
            else:
                form.set_supers(compContacts)
                if thisStudent.primary_contact:
                    supervisorName = thisStudent.primary_contact.fname + " " + thisStudent.primary_contact.lname
                else:
                    supervisorName = comp.team_name
                return render_to_response('work_study/student_timesheet.html', {'supervisor': True,'new': True, 'form': form, 'studentName':\
                    thisStudent, 'supervisorName': supervisorName,}, RequestContext(request, {}))
        else:
            # if student 
            if thisStudent.primary_contact:
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
    fileName = "contract_report.xls"
    
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
    
    report = xlsReport(data, titles, fileName, heading="Contract Report")
    
    return report.finish()
    
    
@user_passes_test(lambda u: u.groups.filter(name='company').count() > 0 or u.is_superuser, login_url='/')    
def change_supervisor(request, studentId):
    thisStudent = StudentWorker.objects.get(id = studentId)
    comp = WorkTeam.objects.filter(login=request.user)[0]
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

@user_passes_test(lambda u: u.groups.filter(name='faculty').count() > 0 or u.is_superuser, login_url='/')    
def report_builder_view(request):
    form = ReportBuilderForm()
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
                return pod_report_work_study(template, students)
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
                elif 'thumbs_fresh' in request.POST:
                    return student_thumbnail(request, 1)
                elif 'thumbs_soph' in request.POST:
                    return student_thumbnail(request, 2)
                elif 'thumbs_jun' in request.POST:
                    return student_thumbnail(request, 3)
                elif 'thumbs_sen' in request.POST:
                    return student_thumbnail(request, 4)
                elif 'history' in request.POST:
                    hist = CompanyHistory.objects.all()
                    data = []
                    for h in hist:
                        data.append([unicode(h.getStudent()), h.placement, h.date])
                    titles = (["Student", "WorkTeam left", "Date",])
                    report = xlsReport(data, titles, "company_history.xls", heading="Company History")
                    return report.finish()
                elif 'hand33' in request.POST:
                    students = StudentWorker.objects.all()
                    data = []
                    titles = ["Student last name", 'Student first name', 'Types']
                    for student in students:
                        handout = Handout33.objects.filter(studentworker=student)
                        traits = []
                        traits.append(student.fname)
                        traits.append(student.lname)
                        for h in handout:
                            traits.append(h)
                        data.append(traits)
                    return xlsReport(data, titles, "Handout_33.xls", heading="Handout33").finish()
                elif 'dols' in request.POST:
                    return dol_xls_report(form.cleaned_data['custom_billing_begin'], form.cleaned_data['custom_billing_end'])
                elif 'contracts' in request.POST:
                    return contracts_report()
                elif 'attnMonday' in request.POST:
                    data = {}
                    for pickup in pickups:
                        data[unicode(pickup)] = {}
                        sheet = data[unicode(pickup)]
                        sheet['$student'] = []
                        sheet['$company'] = []
                        sheet['$train'] = []
                        sheet['$stop'] = []
                        sheet['$cra'] = []
                        sheet['$cell'] = []
                        for stu in StudentWorker.objects.filter(day="M", placement__pickup_location__location=pickup): 
                            sheet['$student'].append(unicode(stu))
                            sheet['$company'].append(unicode(stu.placement))
                            sheet['$train'].append(unicode(stu.placement.train_line))
                            sheet['$stop'].append(unicode(stu.placement.stop_location))
                            sheet['$cra'].append(unicode(stu.placement.cra))
                            try:
                                number = stu.studentnumber_set.filter(type="C")[0]
                            except:
                                number = None
                            sheet['$cell'].append(unicode(number))
                    magic_function(data)
                
                elif 'attendance' in request.POST:
                    attend = Attendance.objects.filter(absence_date__range=(form.cleaned_data['custom_billing_begin'], form.cleaned_data['custom_billing_end']))
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
                        data.append([at.absence_date, at.student.fname, at.student.lname, at.student.year, half, at.reason, makeup, at.fee, billed])
                    
                    fileName = "attendance_report.xls"
                    report = xlsReport(data, titles, fileName, heading="Total")
                    
                    # waived
                    waivers = attend.filter(waive=True)
                    data = []
                    titles = ["Date", "First Name", "Last", "WorkTeam", "Grade", "Total", "comments", "Bill"]
                    for at in waivers:
                        if at.half_day: half = "1/2"
                        else: half = "1"
                        data.append([at.absence_date, at.student.fname, at.student.lname, at.student.placement, at.student.year, half, at.reason, at.fee])
                    report.addSheet(data, titles, heading="Waived")
                    
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
                        data.append([at.absence_date, at.student.fname, at.student.lname, at.student.placement, at.student.year, half, at.reason, at.student.get_day_display(), makeup, at.fee, billed])
                    report.addSheet(data, titles, heading="Pending")
                    
                    # scheduled
                    sced = attend.filter(~Q(makeup_date=None)).filter(waive=None)
                    data = []
                    titles = ["Date", "First Name", "Last", "WorkTeam", "Supervisor", "Grade", "Total", "comments", "Make up date", "Bill"]
                    for at in sced:
                        if at.half_day: half = "1/2"
                        else: half = "1"
                        if at.waive: makeup = "Waived"
                        else: makeup = at.makeup_date
                        data.append([at.absence_date, at.student.fname, at.student.lname, at.student.placement, at.student.primary_contact, at.student.year, half, at.reason, makeup, at.fee])
                    report.addSheet(data, titles, heading="Scheduled")
                    
                    # outstanding bills, sum of student's fee - paid
                    bills = attend.filter(billed=None)
                    summary = bills.values('student').annotate(Sum('fee__value'), Sum('paid')).values('student__fname', 'student__lname', 'fee__value__sum', 'paid__sum')
                    data = []
                    for at in summary:
                        if at['fee__value__sum'] or at['paid__sum']:
                            total_owes = 0
                            if at['fee__value__sum'] and at['paid__sum']:
                                total_owes = at['fee__value__sum'] - at['paid__sum']
                            data.append([at['student__fname'], at['student__lname'], at['fee__value__sum'], at['paid__sum'], total_owes])
                        
                    titles = ["Fname", "Lname", "Total Fee", "Total Paid", "Total owes school (does not include students who were already billed)"]
                    report.addSheet(data, titles, heading="Bill Summary")
                    
                    timesheets = TimeSheet.objects.filter(date__range=(form.cleaned_data['custom_billing_begin'], form.cleaned_data['custom_billing_end']))
                    data = []
                    titles = ["Date", "First Name", "Last", "Grade", "WorkTeam", "Hours", "School Net Pay", "Student Net Pay"]
                    for ts in timesheets:
                        data.append([ts.date, ts.student.fname, ts.student.lname, ts.student.year, ts.company, ts.hours, ts.school_net, ts.student_net])
                    report.addSheet(data, titles, heading="TimeSheets")
                    return report.finish()
                
                # All students and the the number of timesheets submitted for some time period    
                elif 'student_timesheet' in request.POST:
                    data = []
                    titles = ["Student", "Work Day", "Placement", "Number of time sheets submitted", "Dates"]
                    students = StudentWorker.objects.filter(inactive=False)
                    for student in students:
                        ts = TimeSheet.objects.filter(student=student).filter(date__range=(form.cleaned_data['custom_billing_begin'], form.cleaned_data['custom_billing_end']))
                        dates = ""
                        for t in ts:
                            dates += unicode(t.date) + ", "
                        data.append([student, student.day, student.placement, ts.count(), dates])
                    report = xlsReport(data, titles, "Student timesheets.xls", heading="Student Timesheets")
                    return report.finish()
                        
                # billing report for time worked for own pay.
                elif 'billing' in request.POST:
                    timesheets = TimeSheet.objects.filter(Q(date__range=(form.cleaned_data['custom_billing_begin'], form.cleaned_data['custom_billing_end'])) & \
                        Q(for_pay__iexact=1) & Q(approved__iexact=1)).order_by('student', 'date')
                    data = []
                    titles = ["Company", "Work Team", "Student", "", "Date", "Hours Worked", "Student Salary", "Company Bill"]
                    fileName = "Billing_Report.xls"
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
                                data.append(["", "", timesheet.student.fname, timesheet.student.lname, timesheet.date, timesheet.hours, \
                                    timesheet.student_net, timesheet.school_net])
                                studenti += 1
                                # if last day for this student print out the student's totals
                                if studenti == timesheets.filter(company__id__iexact=company.id).filter(student__id__iexact=timesheet.student.id).count():
                                    stu_total = timesheets.filter(company__id__iexact=company.id).filter(student__id__iexact=timesheet.student.id). \
                                        aggregate(Sum('hours'), Sum('student_net'), Sum('school_net'))
                                    data.append(["", "", "", "", "Total", stu_total['hours__sum'], stu_total['student_net__sum'], \
                                        stu_total['school_net__sum']])
                                    total_hours += stu_total['hours__sum']
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
                    report = xlsReport(data, titles, fileName, heading="Detailed Hours")
                    
                    ### WorkTeam Summary
                    data = []
                    comp_totals = timesheets.values('company').annotate(Count('student', distinct=True), Sum('hours'), Avg('hours'), Sum('student_net'), \
                            Sum('school_net')).values('company', 'company__company__name', 'company__team_name', 'student__count', 'hours__sum', 'hours__avg', 'student_net__sum', 'school_net__sum')
                    for c in comp_totals.order_by('company__company'):
                        data.append([c['company__company__name'], c['company__team_name'], c['student__count'], c['hours__sum'], c['hours__avg'], c['student_net__sum'], c['school_net__sum']])
                    titles = ["Company", "WorkTeam", "Workers Hired", "Hours Worked", "Avg Hours per Student", "Gross Amount Paid to Students", "Amount Billed to Company"]
                    report.addSheet(data, titles, heading="Work Team Summary")
                    
                    ### Company Summary
                    data = []
                    comp_totals = timesheets.values('company__company__id').annotate(Count('student', distinct=True), Sum('hours'), Avg('hours'), Sum('student_net'), \
                            Sum('school_net')).values('company__company__name', 'student__count', 'hours__sum', 'hours__avg', 'student_net__sum', 'school_net__sum').order_by('company__company')
                    
                    for c in comp_totals:
                        data.append([c['company__company__name'], c['student__count'], c['hours__sum'], c['hours__avg'], c['student_net__sum'], c['school_net__sum']])
                    titles = ["Company", "Workers Hired", "Hours Worked", "Avg Hours per Student", "Gross Amount Paid to Students", "Amount Billed to Company"]
                    report.addSheet(data, titles, heading="Company Summary")
                    
                    ### Payroll (ADP #s)
                    data = []
                    students = StudentWorker.objects.filter(timesheet__in=timesheets)
                    for student in students:
                        ts = timesheets.filter(student=student).aggregate(Sum('hours'), Sum('student_net'))
                        data.append([student.unique_id, student.fname, student.lname, student.adp_number, ts['hours__sum'], ts['student_net__sum']])
                    titles = ['Unique ID', 'First Name', 'Last Name', 'ADP #', 'Hours Worked', 'Gross Pay']
                    report.addSheet(data, titles, heading="Payroll (ADP #s)")
                    
                    ### Student info wo ADP#
                    data = []
                    for student in students:
                        if not student.adp_number:
                            ts = timesheets.filter(student=student).aggregate(Sum('student_net'))
                            data.append([student.lname, student.fname, student.parent_guardian, student.street, \
                                student.city, student.state, student.zip, student.ssn, ts['student_net__sum']])
                    titles = ['lname', 'fname', 'parent', 'address', 'city', 'state', 'zip', 'ss', 'pay']
                    report.addSheet(data, titles, heading="Student info wo ADP #")
                    
                    return report.finish()
    
                elif 'all_timesheets' in request.POST:
                    timesheets = TimeSheet.objects.all().order_by('student', 'date')
                    data = []
                    titles = ["Name", "", "For Pay", "make up", "approved", "company", "creation date", "date"]
                    fileName = "timesheets.xls"
                    for ts in timesheets:
                        data.append([ts.student.fname, ts.student.lname, ts.for_pay, ts.make_up, ts.approved, ts.company, ts.creation_date, ts.date, ts.time_in, ts.time_lunch, ts.time_lunch_return, ts.time_out, ts.hours, ts.student_net, ts.school_net, ts.student_accomplishment, ts.performance, ts.supervisor_comment])
                    report = xlsReport(data, titles, fileName, heading="timesheets")
                    return report.finish()
                    
                # master contact list
                elif 'master' in request.POST:
                    workers = (StudentWorker.objects.all()).exclude(inactive=True)
                    data = []
                    for worker in workers:
                        try:
                            number = StudentNumber.objects.filter(student=worker).filter(type='Cell')
                        except:
                            try:
                                number = (StudentNumber.object.filter(student=worker))[0]
                            except:
                                number = "none"
                        try:
                            eContacts = (EmergencyContact.objects.filter(student=worker))
                            try:
                                eContact = eContacts.get(primary_contact=True)
                            except:
                                eContact = eContacts[0]
                            eFname = eContact.fname
                            try:
                                eNumbers = EmergencyContactNumber.objects.filter(contact = eContact)
                                if not eNumbers[0]:
                                    eNumbers[0] = ("none")
                                if not eNumbers[1]:
                                    eNumbers[1] = ("none")
                            except:
                                eNumbers = [("none"), ("none")]
                        except:
                            eFname = "No contact assigned"
                            eNumbers = [("none"), ("none")]
                            

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
                        data.append([worker.fname, worker.lname, worker.mname, worker.year, worker.day, supFname,\
                            supLname,supPhone, supCell,supEmail,number,eFname,eNumbers[0],eNumbers[1]])   
                    fileName = "StudentMasterContactList.xls"
                    titles = ['First Name', 'Last Name', 'Middle Name','Year', 'Work Day', 'Supervisor First Name', 'Supervisor Last Name', 'Supervisor Phone', \
                        'Supervisor Cell', 'Supervisor Email', 'Student Cell', 'Parent First Name', 'Parent Number', 'Parent Secondary Number']
                    report = xlsReport(data, titles, fileName, heading="Custom Report")
                    return report.finish()
            else:
                return render_to_response('work_study/reportBuilder.html', {'form': form,'request':request, 'template_form': template_form}, RequestContext(request, {}))
    return render_to_response('work_study/reportBuilder.html', {'form': form,'request':request, 'template_form': template_form}, RequestContext(request, {}))

@user_passes_test(lambda u: u.groups.filter(name='cwsp').count() > 0 or u.is_superuser, login_url='/')    
def dol_form(request, id=None):
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
        return render_to_response('work_study/DOL.html', {'form': form,'request':request}, RequestContext(request, {}))
   
def dol_xls_report(begin_date, end_date,):
    data = []
    titles = ["Work Team", "CRA", "Total visits", "DOL visits (in specified dates)", "DOL visit in active year"]
    fileName = "Client_visit_report.xls"
    
    teams = WorkTeam.objects.all().annotate(Count('clientvisit'))
    for team in teams:
        if team.is_active():
            dols = ClientVisit.objects.filter(company=team, dol=True).order_by('-date')
            if begin_date and end_date:
                dols = dols.filter(date__range=(begin_date, end_date))
            if dols.count() > 0:
                if dols[0].date > SchoolYear.objects.get(active_year=True).start_date:
                    dol_this_year = "Yes, last was " + unicode(dols[0].date)
                else: 
                    dol_this_year = "No, last was " + unicode(dols[0].date)
            else:
                dol_this_year = "None"
            data.append([team.team_name, team.cra, team.clientvisit__count, dols.count(), dol_this_year])
    
    report = xlsReport(data, titles, fileName, heading="Client Visit Report")
    
    return report.finish()

@user_passes_test(lambda u: u.groups.filter(name='faculty').count() > 0 or u.is_superuser, login_url='/')  
def student_meeting(request):
    try:
        start_date = SchoolYear.objects.get(active_year=True).start_date
    except: start_date = None
    meetings = []
    
    for student in StudentWorker.objects.filter(inactive=False):
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
    company = Company.objects.get(id=id)
    
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
            return HttpResponseRedirect('/work_study/company_contract_complete/%s/' % contract.id)
    else:
        form = CompanyContactForm3(instance=contract)
    return render_to_response('work_study/company_contract3.html', {'request': request, 'form':form, 'contact_info': contact_info, 'company':company, 'contract':contract}, RequestContext(request, {}))
    
def company_contract_complete(request, id):
    contract = CompContract.objects.get(id=id)
    company = contract.company
    return render_to_response('work_study/company_contract_complete.html', {'request': request, 'company':company, 'contract':contract}, RequestContext(request, {}))
    
def company_contract_pdf(request, id):
    contract = CompContract.objects.get(id=id)
    
     # Check if using IE
    if re.search('MSIE', request.META['HTTP_USER_AGENT']):
        return contract.get_contract_as_pdf(ie=True)
    else:
        return contract.get_contract_as_pdf()