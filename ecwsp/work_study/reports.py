from django.db import connection
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages

from ecwsp.administration.models import Configuration
from ecwsp.sis.xlsReport import xlsReport
from ecwsp.work_study.xlsReport import customXls
from ecwsp.work_study.models import WorkTeam, TimeSheet, StudentWorker, PickupLocation, StudentWorkerRoute

import xlwt as pycel
import datetime

days = (["Monday", "M"], ["Tuesday","T"], ["Wednesday","W"], ["Thursday","TH"], ["Friday", "F"])

def fte_by_ind(request):
    """ FTE by industry
    """
    fileName = "report_fteByInd.xls"
    cursor = connection.cursor()
    fte = int(Configuration.get_or_default(name="Students per FTE"[0], default=5).value)
    cursor.execute("select industry_type, count(*)/" + str(fte) + \
        " from work_study_studentworker left join work_study_workteam on work_study_workteam.id = "+\
        "work_study_studentworker.placement_id where work_study_workteam.inactive = False group by industry_type;")
    names = cursor.fetchall()
    titles = (["Industry", "FTE"])
    report = xlsReport(names, titles, fileName, heading="FTE by Industry Type")
    report.addSheet(student_company_day_report(industry_type=True), heading="Detail")
    return report.finish()


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


def fte_by_day(request):
    fileName = "report_fteByDay.xls"
    cursor = connection.cursor()
    fte = int(Configuration.get_or_default(name="Students per FTE"[0], default=5).value)
    cursor.execute("select day, count(*)/" + str(fte) + \
        " from work_study_studentworker left join work_study_workteam on work_study_workteam.id = "+\
        "work_study_studentworker.placement_id where work_study_workteam.inactive = False group by day;")
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
            students = StudentWorker.objects.filter(day=day[1], placement__pm_transport_group__location=pickup).filter(inactive=False)
        else:
            students = StudentWorker.objects.filter(day=day[1], placement__am_transport_group__location=pickup).filter(inactive=False)
        for stu in students:
            if stu.fax:
                ws.write(y,0,"txt", myFontStyle)                            #Small font fax.
            else:
                ws.write(y,0," ", myFontStyle)                                #blank for absent/late
            ws.write(y,1,unicode(stu.fname + " " +stu.lname), myFontStyle)    #name
            ws.write(y,2,unicode(stu.placement), myFontStyle)                #placement
            ws.write(y,3,unicode(stu.placement.travel_route), myFontStyle)    #train line
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
    cursor.execute("select paying, count(*)/" + str(student_fte) + \
                   " from work_study_studentworker left join work_study_workteam on work_study_workteam.id = "+\
        "work_study_studentworker.placement_id where work_study_workteam.inactive = False group by paying;")
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


def route_attendance(request):
    data = []
    titles = ['Student First', 'Last', 'Route','Van','Company','Notes']
    fileName = "route_attendance.xls"
    for ts in timesheets:
        data.append([])
    report = xlsReport(data, titles, fileName, heading="Route_Attendance")
    return report.finish()
        

def am_route_attendance(request):
    # TO DO Impliment workday selection!!!!
    data = []
    titles = ["Company", "Address", "City", "State", "Zip", "Contact First", "Contact Last",
              "Phone", "Grade",'Workday','Gender','Student First','Student Last',
              'Cell','Earliest','Latest','Ideal','Schedule', datetime.date.today(), 'Notes']
    report = None
    if 'am_route_attendance' in request.POST:
        fileName = "AM_Routes.xls"
    else:
        fileName = "PM_Routes.xls"
    if not StudentWorkerRoute.objects.all():
        messages.error(request, 'You must create at least one route before running this report!')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))
    for route in StudentWorkerRoute.objects.all():
        data = []
        if 'am_route_attendance' in request.POST:
            students =  StudentWorker.objects.filter(am_route=route)
        else:
            students =  StudentWorker.objects.filter(pm_route=route)
        for student in students:
            row = []
            if hasattr(student,'placement') and student.placement:
                row += [
                    student.placement,
                    student.placement.address,
                    student.placement.city,
                    student.placement.state,
                    student.placement.zip,
                    ]
            else:
                row += ['', '', '', '', '']
            if hasattr(student,'primary_contact') and student.primary_contact:
                row += [
                    student.primary_contact.fname,
                    student.primary_contact.lname,
                    student.primary_contact.phone,
                ]
            else:
                row += ['', '', '']
            row += [
                student.year,
                student.day,
                student.sex,
                student.fname,
                student.lname,
                student.phone,
            ]
            if hasattr(student,'placement') and student.placement:
                row += [
                    student.placement.time_earliest,
                    student.placement.time_latest,
                    student.placement.time_ideal,
                    student.placement.am_transport_group,
                    student.placement.directions_to,
                ]
            else:
                row += ['', '', '', '','']
            row += [student.get_transport_exception_display(), ]
            data.append(row)
        if not report:
            report = xlsReport(data, titles, fileName, heading=unicode(route))
        else:
            report.addSheet(data, titles, heading=unicode(route))
    return report.finish()