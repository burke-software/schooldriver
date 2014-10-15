from ecwsp.volunteer_track.models import Volunteer
from ecwsp.administration.models import Configuration
from ecwsp.sis.helper_functions import all_tenants
from django.core.mail import send_mail
from django.conf import settings
from datetime import date

from celery.task.schedules import crontab
from celery.decorators import periodic_task
from django_sis.celery import app

@app.task
@all_tenants
def handle():
    """ Emails subscribed volunteer managers daily site submissions
    """
    volunteers = Volunteer.objects.filter(email_queue__isnull=False).exclude(email_queue="")
    if volunteers:
        from_email = Configuration.objects.get_or_create(name="From Email Address")[0].value
        to_emails = Configuration.get_or_default("Volunteer Track Manager Emails", default="").value
        msg = "Student(s): \n"
        subject = "SWORD daily volunteer changes"

        for volunteer in volunteers:
            msg += "%s - %s\n\n" % (volunteer, volunteer.email_queue)

        to_emails = to_emails.split(',')
        sane_to_emails = []
        for email in to_emails:
            if email and email != " ":
                sane_to_emails.append(email.strip())
        send_mail(subject, msg, from_email, sane_to_emails)

        for volunteer in volunteers:
            volunteer.email_queue = ""
            volunteer.save()
