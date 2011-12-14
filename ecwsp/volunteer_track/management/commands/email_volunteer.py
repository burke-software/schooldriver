from ecwsp.volunteer_track.models import *
from ecwsp.administration.models import Configuration
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from datetime import date

class Command(BaseCommand):
    help = 'Emails subscribed volunteer managers daily site submissions, should be used with cron'
    
    def handle(self, *args, **options):
        # email student interactions
        volunteers = Volunteer.objects.filter(email_queue__is_null=False).exclude(email_queue="")
        if volunteers:
            from_email = Configuration.objects.get_or_create(name="From Email Address")[0].value
            to_emails = Configuration.get_or_default("Volunteer Track Manager Emails", default="").value
            msg = "Student(s): \n"
            subject = "SWORD daily volunteer changes"
            
            for volunteer in volunteers:
                msg += "%s - %s\n\n" % (volunteer, volunteer.email_queue)
            
            send_mail(subject, msg, from_email, to_emails.split(','))
            
            for volunteer in volunteers:
                volunteer.email_queue = ""
                
