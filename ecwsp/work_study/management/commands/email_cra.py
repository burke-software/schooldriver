from ecwsp.work_study.models import *
from ecwsp.administration.models import Configuration
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from datetime import date

class Command(BaseCommand):
    help = 'Emails subscribed cra\'s daily comments, should be used with cron'
    
    def handle(self, *args, **options):
        # email student interactions
        from_email = Configuration.objects.get_or_create(name="From Email Address")[0].value
        cras = CraContact.objects.filter(email=True)
        for cra in cras:
            msg = "Student(s): "
            subject = "SWORD student interactions"
            interactions = StudentInteraction.objects.filter(date__year=date.today().year, date__day=date.today().day, date__month=date.today().month).filter(student__placement__cras=cra)
            if interactions.count() > 0:
                for interaction in interactions:
                    for student in interaction.student.all():
                        msg += unicode(student) + " "
                    msg += "\n"
                    msg += interaction.comments
                    msg += "\n"
                    for preset in interaction.preset_comment.all():
                        msg += unicode(preset) + "\n"
                    send_mail(subject, msg, from_email, [unicode(cra.name.email)])
        
        cras = CraContact.objects.filter(email=True).filter(email_all=False)
        for cra in cras:
            msg = ""
            subject = "SWORD comments"
            send = False
            timesheets = TimeSheet.objects.filter(company__cras=cra).filter(creation_date__year=date.today().year, creation_date__day=date.today().day, creation_date__month=date.today().month)
            if timesheets.count() > 0:
                for timesheet in timesheets:
                    if timesheet.supervisor_comment or timesheet.performance or timesheet.student_accomplishment:
                        send = True
                        if timesheet.show_student_comments:
                            showtxt = "Student was able to view comments"
                        else:
                            showtxt = "Student was not allowed to view comments"
                        msg += unicode(timesheet.student) + ": " + unicode(timesheet.performance) + "\nsupervisor: " + \
                            unicode(timesheet.company) + " - " + unicode(timesheet.student.primary_contact) + "\n" + \
                            unicode(timesheet.supervisor_comment) + "\nstudent: " + unicode(timesheet.student_accomplishment) + \
                            showtxt + "\n"
                        if timesheet.approved:
                            msg += "Timesheet approved by supervisor\n\n"
                        else:
                            msg += "Timesheet not yet approved by supervisor\n\n"
                send_mail(subject, msg, from_email, [unicode(cra.name.email)])
        cras = CraContact.objects.filter(email_all=True)
        for cra in cras:
            msg = ""
            subject = "SWORD comments"
            send = False
            timesheets = TimeSheet.objects.filter(creation_date__year=date.today().year, creation_date__day=date.today().day, creation_date__month=date.today().month)
            if timesheets.count() > 0:
                for timesheet in timesheets:
                    if timesheet.supervisor_comment or timesheet.performance or timesheet.student_accomplishment:
                        send = True
                        msg += unicode(timesheet.student) + ": " + unicode(timesheet.performance) + "\nsupervisor: " + \
                            unicode(timesheet.company) + " - " + unicode(timesheet.student.primary_contact) + "\n" + \
                            unicode(timesheet.supervisor_comment) + "\nstudent: " + unicode(timesheet.student_accomplishment) + "\n"
                        if timesheet.approved:
                            msg += "Timesheet approved by supervisor\n\n"
                        else:
                            msg += "Timesheet not yet approved by supervisor\n\n"
                send_mail(subject, msg, from_email, [unicode(cra.name.email)])
