from ecwsp.work_study.models import StudentInteraction, CraContact, TimeSheet
from ecwsp.administration.models import Configuration
from django.core.mail import send_mail
from datetime import date
from django.conf import settings

from celery.task.schedules import crontab
from celery.decorators import periodic_task
from celery import task

if 'ecwsp.work_study' in settings.INSTALLED_APPS:
    
    if settings.SYNC_SUGAR:
        from ecwsp.work_study.sugar_sync import SugarSync
        modify_date_minutes = int(Configuration.get_or_default("sync sugarcrm minutes",default="30").value)
        @periodic_task(run_every=crontab(minute='*/%s' % (modify_date_minutes,)))
        def update_contacts_from_sugarcrm():
            sugar_sync = SugarSync()
            sugar_sync.update_contacts_from_sugarcrm()
        
        @task()
        def update_contact_to_sugarcrm(contact):
            sugar_sync = SugarSync()
            sugar_sync.update_contact(contact)
    
    @periodic_task(run_every=crontab(hour=20, minute=27))
    def email_cra_nightly():
        """ Email CRA nightly time sheet and student interaction information
        """
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
            timesheets = TimeSheet.objects.filter(company__cras=cra).filter(creation_date__year=date.today().year, creation_date__day=date.today().day, creation_date__month=date.today().month).order_by('company__team_name')
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
            timesheets = TimeSheet.objects.filter(creation_date__year=date.today().year, creation_date__day=date.today().day, creation_date__month=date.today().month).order_by('company__cras','company__team_name')
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
