from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core import urlresolvers
from django.contrib.auth.models import User

from models import *
from ecwsp.sis.models import SchoolYear
from ecwsp.administration.models import *
from ecwsp.sis.lookups import StudentLookup

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
    def format_item_display(self,student):
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
            for infr in Infraction.objects.all():
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