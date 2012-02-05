from ajax_select import LookupChannel
from ecwsp.sis.lookups import StudentLookup
from models import *
from ecwsp.sis.models import SchoolYear

import datetime

class AttendanceStudentLookup(StudentLookup):
    def format_item_display(self,student):
        output = "<table style=\"border-collapse: collapse;\"><tr><td><img style=\"height:30px;\" src=%s></td><td>%s %s</td></tr></table>" \
            % (student.pic.url_70x65, student.fname, student.lname)
        
        output += "<table style=\"width: 100%;\"><tr>"
        school_start = SchoolYear.objects.get(active_year=True).start_date
        school_end = SchoolYear.objects.get(active_year=True).end_date
        attendances = StudentAttendance.objects.filter(student=student, date__range=(school_start, school_end))
        absences = attendances.filter(status__absent=True).count()
        tardies = attendances.filter(status__tardy=True).count()
        output += "<td>Total absences: %s</td></tr><tr><td>Total tardies: %s</td></tr>" % (absences, tardies)
        for attendance in attendances:
            output += "<tr><td>" + unicode(attendance.date) + " " + unicode(attendance.status) + ": " + unicode(attendance.notes) + "</td></tr>"
        output += "</table>"  
        return output
        
        
class AttendanceAddStudentLookup(StudentLookup):
    def format_item_display(self,student):
        output = "<table style=\"border-collapse: collapse;\"><tr><td><img style=\"height:30px;\" src=%s></td><td>%s %s</td></tr></table>" \
            % (student.pic.url_70x65, student.fname, student.lname)
        
        output += "<table style=\"width: 100%;\">"
        attendances = StudentAttendance.objects.filter(student=student, date=datetime.datetime.now())
        for attendance in attendances:
            output += "<tr><td>" + unicode(attendance.date) + " " + unicode(attendance.status) + ": " + unicode(attendance.notes) + "</td></tr>"
        output += "</table>"  
        return output
