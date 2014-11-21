from ecwsp.work_study.models import StudentInteraction, CraContact, TimeSheet, StudentWorker
from ecwsp.administration.models import Configuration
from ecwsp.sis.helper_functions import all_tenants
from django.core.mail import send_mail
from django.utils.encoding import smart_unicode
from datetime import date
import logging
from django.conf import settings
from constance import config

from celery import task
from django_sis.celery import app

import sys

from ecwsp.work_study.sugar_sync import SugarSync
modify_date_minutes = config.SUGAR_SYNC_MINUTES

@app.task
@all_tenants
def update_contacts_from_sugarcrm():
    if config.SUGAR_SYNC:
        sugar_sync = SugarSync()
        sugar_sync.update_contacts_from_sugarcrm()

@app.task
def update_contact_to_sugarcrm(contact):
    if config.SUGAR_SYNC:
        sugar_sync = SugarSync()
        sugar_sync.update_contact(contact)

@app.task
@all_tenants
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
                try:
                    send_mail(subject, msg, from_email, [unicode(cra.name.email)])
                except:
                    logging.warning('Could not email interactions', exc_info=True, extra={
                        'exception': sys.exc_info()[0],
                        'exception2': sys.exc_info()[1],
                    })

    cras = CraContact.objects.filter(email=True).filter(email_all=False)
    for cra in cras:
        msg = ""
        subject = "SWORD comments"
        send = False
        timesheets = TimeSheet.objects.filter(company__cras=cra).filter(cra_email_sent=False, creation_date__month=date.today().month).order_by('company__team_name')
        if timesheets.count():
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
                        "\n" + showtxt + "\n"
                    if timesheet.approved:
                        msg += "Timesheet approved by supervisor\n\n"
                    else:
                        msg += "Timesheet not yet approved by supervisor\n\n"

            # Now get students who are present but did not submit a time card
            students = StudentWorker.objects.filter(attendance__absence_date=date.today(),attendance__tardy="P").exclude(timesheet__date=date.today())
            if students:
                msg += "The following students were present but did not submit time sheets:\n"
                for student in students:
                    msg += smart_unicode(student) + ", "
                msg = msg[:-2]

            try:
                send_mail(subject, msg, from_email, [unicode(cra.name.email)])
            except:
                logging.warning('Could not email CRA', exc_info=True, extra={
                    'exception': sys.exc_info()[0],
                    'exception2': sys.exc_info()[1],
                })
    cras = CraContact.objects.filter(email_all=True)
    for cra in cras:
        msg = ""
        subject = "SWORD comments"
        send = False
        timesheets = TimeSheet.objects.filter(cra_email_sent=False, creation_date__month=date.today().month).order_by('company__cras','company__team_name')
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

            # Now get students who are present but did not submit a time card
            students = StudentWorker.objects.filter(attendance__absence_date=date.today(),attendance__tardy="P").exclude(timesheet__date=date.today())
            if students:
                msg += "The following students were present but did not submit time sheets:\n"
                for student in students:
                    msg += smart_unicode(student) + ", "
                msg = msg[:-2]

            try:
                send_mail(subject, msg, from_email, [unicode(cra.name.email)])
            except:
                logging.warning('Could not email CRA all comments', exc_info=True, extra={
                    'exception': sys.exc_info()[0],
                    'exception2': sys.exc_info()[1],
                })

    # Check off time sheets that were processed today (so they aren't processed tomorrow)
    timesheets = TimeSheet.objects.filter(creation_date__month=date.today().month, cra_email_sent=False)
    for timesheet in timesheets:
        timesheet.cra_email_sent = True
        timesheet.save()

    # Remind students to submit time sheets
    students = StudentWorker.objects.filter(attendance__absence_date=date.today(),attendance__tardy="P").exclude(timesheet__date=date.today())
    subject = "Timesheet not submitted"
    for student in students:
        msg = u"Hello {0},\n".format(student.first_name)
        conf_msg = Configuration.get_or_default(
            "work_study message to student missing time sheet",
            default="You did not submit a time card today. Please remember to do so. This is an automated message, please do not reply.")
        msg += conf_msg.value
        email = student.get_email
        if email and email[-9:] != "change.me":
            try:
                send_mail(subject, msg, from_email, [unicode(email)])
            except:
                logging.warning('Could not email student about missing time card', exc_info=True, extra={
                    'exception': sys.exc_info()[0],
                    'exception2': sys.exc_info()[1],
                })
