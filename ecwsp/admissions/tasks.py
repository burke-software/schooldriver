from ecwsp.admissions.models import Applicant
from ecwsp.administration.models import Configuration
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
import datetime
import logging
from django.conf import settings

from celery.task.schedules import crontab
from celery.decorators import periodic_task
from celery import task

import sys

if 'ecwsp.admissions' in settings.INSTALLED_APPS:
    
    @periodic_task(run_every=crontab(hour=22, minute=43))
    def email_admissions_new_inquiries():
        """ Email Admissions team about new online inquiries
        """
        from_email = Configuration.get_or_default("From Email Address").value
        to_email = Configuration.get_or_default('admissions_notify_email').value
        subject = "New online inquiries"
        today = datetime.date.today()
        
        new_inquiries = Applicant.objects.filter(date_added=today, from_online_inquiry=True)
        if new_inquiries:
            msg = "The following inquiries were submitted today\n"
            for inquiry in new_inquiries:
                msg += '\n<a href="{0}{1}">{2} {3}</a>\n'.format(
                    settings.BASE_URL,
                    reverse('admin:admissions_applicant_change', args=(inquiry.id,)),
                    inquiry.fname,
                    inquiry.lname)
                if Applicant.objects.filter(fname=inquiry.fname, lname=inquiry.lname).count() > 1:
                    msg += "(May be duplicate)\n"
                
            send_mail(subject, msg, from_email, to_email.split(','))
