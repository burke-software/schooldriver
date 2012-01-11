from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core import urlresolvers
from django.contrib.auth.models import User
from django.utils.html import escape
from ajax_select import LookupChannel

from ecwsp.sis.models import *
from ecwsp.administration.models import *

from datetime import date

class StudentLookup(LookupChannel):
    model = Student
    
    def get_query(self,q,request):
        qs = Student.objects.all()
        if not UserPreference.objects.get_or_create(user=request.user)[0].include_deleted_students:
            qs = qs.filter(inactive=False)
        for word in q.split():
            qs = qs.filter(Q(lname__icontains=word) | Q(fname__icontains=word))
        return qs.order_by('lname')

    def format_match(self,student):
        year = student.year
        if not year: year = "Unknown year"
        image = student.pic.url_70x65
        if not image: image = "/static/images/noimage.jpg"
        return '<div style="width:250px; min-height:53px;"><img style="float:left; margin-right: 3px;" src=%s> %s %s <br/> %s </div>' \
            % (image, student.fname, student.lname, year)

    def format_item_display(self,student):
        year = student.year
        if not year: year = "Unknown year"
        image = student.pic.url_70x65
        if not image: image = "/static/images/noimage.jpg"
        return '<div style="min-width:250px; min-height:53px;"><img style="float:left; margin-right: 3px;" src=%s> %s %s <br/> %s </div><div/>' \
            % (image, student.fname, student.lname, year) 

    def get_objects(self,ids):
        return Student.objects.filter(pk__in=ids).order_by('lname')


class AllStudentLookup(StudentLookup):
    """ Always looks up inactive students too """
    def get_query(self,q,request):
        qs = Student.objects.all()
        for word in q.split():
            qs = qs.filter(Q(lname__icontains=word) | Q(fname__icontains=word))
        return qs.order_by('lname')

class StudentLookupSmall(StudentLookup):
    def format_match(self,student):
        year = student.year
        if not year: year = "Unknown year"
        image = student.pic.url_70x65
        if not image: image = "/static/images/noimage.jpg"
        return "<table style=\"border-collapse: collapse;\"><tr><td><img style=\"height:30px;\" src=%s></td><td>%s %s<br/>%s</td></tr></table>" \
            % (image, student.fname, student.lname, year)

    def format_item_display(self,student):
        return "%s %s" % (student.fname, student.lname)


class EmergencyContactLookup(LookupChannel):
    model = EmergencyContact
    
    def get_query(self,q,request):
        qs = EmergencyContact.objects.all()
        for word in q.split():
            qs = qs.filter(Q(lname__icontains=word) | Q(fname__icontains=word))
        return qs.order_by('lname')

    def format_item_display(self,emergency_contact):
        if emergency_contact.emergency_only:
            result = "<table style=\"width: auto;\"><tr><td colspan=3><a href=\"/admin/sis/emergencycontact/%s/\" target=\"_blank\">%s %s - %s (Emergency only)</a></td></tr>" \
                % (emergency_contact.id, emergency_contact.fname, emergency_contact.lname, emergency_contact.relationship_to_student)
        elif emergency_contact.primary_contact:
            result = "<table style=\"width: auto;\"><tr><td colspan=3><a href=\"/admin/sis/emergencycontact/%s/\" target=\"_blank\"><span style=\"font-weight: bold;\">%s %s</span> - %s<br/>%s<br/>%s %s %s</a></td></tr>" \
                % (emergency_contact.id, emergency_contact.fname, emergency_contact.lname, emergency_contact.relationship_to_student, emergency_contact.street, emergency_contact.city,
                   emergency_contact.state, emergency_contact.zip)
        else:
            result = "<table style=\"width: auto;\"><tr><td colspan=3><a href=\"/admin/sis/emergencycontact/%s/\" target=\"_blank\">%s %s - %s</a></td></tr>" \
                % (emergency_contact.id, emergency_contact.fname, emergency_contact.lname, emergency_contact.relationship_to_student)
        for number in emergency_contact.emergencycontactnumber_set.all():
            result += "<tr><td style=\"border-bottom: none;\"> %s </td><td style=\"border-bottom: none;\"> %s </td></tr>" % (number.full_number(), number.get_type_display())
        result += "</table>"
        return result
    
    def get_objects(self,ids):
        return EmergencyContact.objects.filter(pk__in=ids).order_by('-primary_contact', 'emergency_only', 'lname')
    
    
class FacultyLookup(LookupChannel):
    def get_query(self,q,request):
        qs = Faculty.objects.all()
        for word in q.split():
            qs = qs.filter(Q(lname__icontains=word) | Q(fname__icontains=word) | Q(username__istartswith=q))
        return qs.order_by('lname')

    def get_objects(self,ids):
        return Faculty.objects.filter(pk__in=ids).order_by('lname')

class FacultyUserLookup(object):
    def get_query(self,q,request):
        words = q.split()
        result = User.objects.filter(groups__name="faculty").filter(Q(first_name__istartswith=q) | Q(last_name__istartswith=q) | Q(username__istartswith=q))
        return result

    def format_result(self, faculty):
        return "%s %s" % (faculty.first_name, faculty.last_name)

    def format_item(self,faculty):
        return "%s %s" % (faculty.first_name, faculty.last_name)

    def get_objects(self,ids):
        return User.objects.filter(pk__in=ids).order_by('last_name')
    
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
        attendances = StudentAttendance.objects.filter(student=student, date=datetime.now())
        for attendance in attendances:
            output += "<tr><td>" + unicode(attendance.date) + " " + unicode(attendance.status) + ": " + unicode(attendance.notes) + "</td></tr>"
        output += "</table>"  
        return output
