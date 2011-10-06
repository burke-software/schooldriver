from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core import urlresolvers

from ecwsp.sis.models import *
from ecwsp.administration.models import *

from datetime import date

class StudentLookup(object):
    def get_query(self,q,request):
        """ return a query set.  you also have access to request.user if needed """
        if not request.user.has_perm('sis.view_student'):
            return Student.objects.none()  # Rather than 500 error, just return nothing.
        
        words = q.split()
        # if there is a space
        if (len(words) == 2):
            # search based on first or last name in either order with space in between.
            result = Student.objects.filter(Q(Q(fname__istartswith=words[0]) & Q(lname__istartswith=words[1]) | Q(fname__istartswith=words[1]) & Q(lname__istartswith=words[0])))
        # if all one word (or technically more but this will fail)
        else:
            result = Student.objects.filter(Q(fname__istartswith=q) | Q(lname__istartswith=q) | Q(username__icontains=q))
        pref = UserPreference.objects.get_or_create(user=request.user)[0]
        if pref.include_deleted_students:
            return result
        return result.filter(inactive=False)

    def format_result(self,student):
        """ 
        the search results display in the dropdown menu.  may contain html and multiple-lines. will remove any |  
        Null's will break this, so check everything and replace it with something meaningful before return 
        """
        year = student.year
        if not year: year = "Unknown year"
        image = student.pic.url_70x65
        if not image: image = "/static/images/noimage.jpg"
        return "<table style=\"border-collapse: collapse;\"><tr><td><img style=\"height:30px;\" src=%s></td><td>%s %s<br/>%s</td></tr></table>" \
            % (image, student.fname, student.lname, year)

    def format_item(self,student):
        """ the display of a currently selected object in the area below the search box. html is OK """
        year = student.year
        if not year: year = "Unknown year"
        image = student.pic.url_70x65
        if not image: image = "/static/images/noimage.jpg"
        return "<table style=\"border-collapse: collapse;\"><tr><td><img src=%s></td><td><a href=\"/admin/sis/student/%s/\" target=\"_blank\">%s %s</a><br/>%s</td></tr></table>" \
            % (image, student.id, student.fname, student.lname, year)

    def get_objects(self,ids):
        """ given a list of ids, return the objects ordered as you would like them on the admin page.
            this is for displaying the currently selected items (in the case of a ManyToMany field)
        """
        return Student.objects.filter(pk__in=ids).order_by('lname')


class AllStudentLookup(StudentLookup):
    def get_query(self,q,request):
        """ return a query set.  you also have access to request.user if needed """
        words = q.split()
        # if there is a space
        if (len(words) == 2):
            # search based on first or last name in either order with space in between.
            result = Student.objects.filter(Q(Q(fname__istartswith=words[0]) & Q(lname__istartswith=words[1]) | Q(fname__istartswith=words[1]) & Q(lname__istartswith=words[0])))
        # if all one word (or technically more but this will fail)
        else:
            result = Student.objects.filter(Q(fname__istartswith=q) | Q(lname__istartswith=q) | Q(username__icontains=q))
        return result

class StudentLookupSmall(StudentLookup):
    def format_result(self,student):
        year = student.year
        if not year: year = "Unknown year"
        image = student.pic.url_70x65
        if not image: image = "/static/images/noimage.jpg"
        return "<table style=\"border-collapse: collapse;\"><tr><td><img style=\"height:30px;\" src=%s></td><td>%s %s<br/>%s</td></tr></table>" \
            % (image, student.fname, student.lname, year)

    def format_item(self,student):
        return "%s %s" % (student.fname, student.lname)

    def get_objects(self,ids):
        return Student.objects.filter(pk__in=ids).order_by('lname')


class StudentWithDisciplineLookup(StudentLookup):
    def format_item(self,student):
        year = student.year
        if not year: year = "Unknown year"
        image = student.pic.url_70x65
        if not image: image = "/static/images/noimage.jpg"
        school_start = SchoolYear.objects.get(active_year=True).start_date
        school_end = SchoolYear.objects.get(active_year=True).end_date
        priors = StudentDiscipline.objects.filter(students=student).filter(date__range=(school_start, school_end))
        output = "<table style=\"border-collapse: collapse; width:700px;\"><tr><td><img style=\"height:30px;\" src=%s></td><td>%s %s <br/><a href=\"/sis/disc/report/%s\">View full report</a>" \
            % (image, student.fname, student.lname, student.id) 
        for prior in priors:
            output += "<br/>%s - %s - %s - %s" % (prior.date.strftime('%b %d, %Y'), prior.infraction, prior.all_actions(), prior.comments)
        output += "</td></tr></table>"
        return output

    def get_objects(self,ids):
        return Student.objects.filter(pk__in=ids).order_by('lname')


class DisciplineViewStudentLookup(StudentLookup):
    def format_item(self,student):
        year = student.year
        if not year: year = "Unknown year"
        image = student.pic.url_70x65
        if not image: image = "/static/images/noimage.jpg"
        priors = StudentDiscipline.objects.filter(students=student)
        output = "<table style=\"border-collapse: collapse;\"><tr><td><img style=\"height:30px;\" src=%s></td><td>%s %s <br/><a href=\"/sis/disc/report/%s\">View full report</a></td></tr></table>" \
            % (image, student.fname, student.lname, student.id) 
        if priors.count() >= 1:
            
            try:
                year = SchoolYear.objects.get(active_year=True)
            except:
                year = " (no active year set) "
            
            output += "<br/><br/><br/><table><tr><th> Discipline statistics for " + unicode(year) + " </th></tr>"
            
            # quick stats
            output += '<tr><td style="font-style:oblique;text-align:center;"> Action Totals </td></tr>'
            for action in DisciplineAction.objects.all():
                action_discipline = DisciplineActionInstance.objects.filter(action__name=action, student_discipline__students=student)
                count = 0;
                for x in action_discipline:
                    count += x.quantity     
                if count > 0:
                    output += "<tr><td> %s: %s </td></tr>" % (action, count)
            output += '<tr><td style="font-style:oblique;text-align:center;"> Infraction Totals </td></tr>'
            for infr in PresetComment.objects.all():
                infr_discipline = priors.filter(infraction=infr)
                if infr_discipline.count() > 0:
                    output += "<tr><td> %s: %s </td></tr>" % (infr, infr_discipline.count()) 
                        
            output += "<table style=\"border-collapse: collapse; width: 777px;\">" + \
                "<tr><th>Date</th><th>Teacher</th><th>Infraction</th><th>Action</th><th>Comments</th></tr>"
            for prior in priors:
                output += "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>" % (prior.date.strftime('%b %d, %Y'), prior.teacher, prior.infraction, prior.all_actions(), prior.comments)
            output += "</tr></table><br/>"
        else:
            output += "<table><tr><td>No discipline history for this student</td></tr></table>"
        return output


class EmergencyContactLookup(object):
    def get_query(self,q,request):
        words = q.split()
        # if there is a space
        if (len(words) == 2):
            # search based on first or last name in either order with space in between.
            result = EmergencyContact.objects.filter(Q(Q(fname__istartswith=words[0]) & Q(lname__istartswith=words[1]) | Q(fname__istartswith=words[1]) & Q(lname__istartswith=words[0])))
        # if all one word (or technically more but this will fail)
        else:
            result = EmergencyContact.objects.filter(Q(fname__istartswith=q) | Q(lname__istartswith=q))
        return result

    def format_result(self, emergency_contact):
        return "%s %s - %s" % (emergency_contact.fname, emergency_contact.lname, emergency_contact.relationship_to_student)

    def format_item(self,emergency_contact):
        if emergency_contact.emergency_only:
            result = "<table style=\"width: auto;\"><tr><td colspan=3><a href=\"/admin/sis/emergencycontact/%s/\" target=\"_blank\">%s %s - %s (Emergency only)</a></td></tr>" \
                % (emergency_contact.id, emergency_contact.fname, emergency_contact.lname, emergency_contact.relationship_to_student)
        elif emergency_contact.primary_contact:
            result = "<table style=\"width: auto;\"><tr><td colspan=3 style=\"font-weight: bold;\"><a href=\"/admin/sis/emergencycontact/%s/\" target=\"_blank\">%s %s - %s</a></td></tr>" \
                % (emergency_contact.id, emergency_contact.fname, emergency_contact.lname, emergency_contact.relationship_to_student)
        else:
            result = "<table style=\"width: auto;\"><tr><td colspan=3><a href=\"/admin/sis/emergencycontact/%s/\" target=\"_blank\">%s %s - %s</a></td></tr>" \
                % (emergency_contact.id, emergency_contact.fname, emergency_contact.lname, emergency_contact.relationship_to_student)
        for number in emergency_contact.emergencycontactnumber_set.all():
            result += "<tr><td style=\"border-bottom: none;\"> %s </td><td style=\"border-bottom: none;\"> %s </td></tr>" % (number.full_number(), number.get_type_display())
        result += "</table>"
        return result
    
    def get_objects(self,ids):
        return EmergencyContact.objects.filter(pk__in=ids).order_by('-primary_contact', 'emergency_only', 'lname')
    
    
class FacultyLookup(object):
    def get_query(self,q,request):
        words = q.split()
        result = Faculty.objects.filter(Q(fname__istartswith=q) | Q(lname__istartswith=q) | Q(username__istartswith=q))
        return result

    def format_result(self, faculty):
        return "%s %s" % (faculty.fname, faculty.lname)

    def format_item(self,faculty):
        return "%s %s" % (faculty.fname, faculty.lname)

    def get_objects(self,ids):
        return Faculty.objects.filter(pk__in=ids).order_by('lname')
        
    
class AttendanceStudentLookup(StudentLookup):
    def format_item(self,student):
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
    def format_item(self,student):
        output = "<table style=\"border-collapse: collapse;\"><tr><td><img style=\"height:30px;\" src=%s></td><td>%s %s</td></tr></table>" \
            % (student.pic.url_70x65, student.fname, student.lname)
        
        output += "<table style=\"width: 100%;\">"
        attendances = StudentAttendance.objects.filter(student=student, date=datetime.now())
        for attendance in attendances:
            output += "<tr><td>" + unicode(attendance.date) + " " + unicode(attendance.status) + ": " + unicode(attendance.notes) + "</td></tr>"
        output += "</table>"  
        return output
