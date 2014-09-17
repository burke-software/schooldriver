from ecwsp.admissions.models import Applicant
from ecwsp.administration.models import Configuration
from ecwsp.sis.helper_functions import all_tenants
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
import datetime
import logging
from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from ecwsp.sis.helper_functions import get_base_url
from django_sis.celery import app

import sys

@app.task
@all_tenants
def email_admissions_new_inquiries():
    """ Email Admissions team about new online inquiries
    """
    from_email = Configuration.get_or_default("From Email Address").value
    to_email = Configuration.get_or_default('admissions_notify_email').value
    if not len(to_email):
        # don't complain if no one wants this report, just quit
        return
    # validate the from address
    try:
        validate_email(from_email)
    except ValidationError:
        logging.warning('email_admissions_new_inquiries failed because of invalid From Email Address "{}"'.format(from_email), exc_info=True)
        return
    # validate the to addresses
    to_email_list = []
    for addr in to_email.split(','):
        try:
            validate_email(addr)
            to_email_list.append(addr)
        except ValidationError:
            logging.warning('email_admissions_new_inquiries omitting invalid address "{}" in admissions_notify_email'.format(addr), exc_info=True)

    subject = "New online inquiries"
    today = datetime.date.today()

    new_inquiries = Applicant.objects.filter(date_added=today, from_online_inquiry=True)
    if new_inquiries:
        msg = "The following inquiries were submitted today\n"
        for inquiry in new_inquiries:
            msg += '\n<a href="{0}{1}">{2} {3}</a>\n'.format(
                get_base_url(),
                reverse('admin:admissions_applicant_change', args=(inquiry.id,)),
                inquiry.fname,
                inquiry.lname)
            if Applicant.objects.filter(fname=inquiry.fname, lname=inquiry.lname).count() > 1:
                msg += "(May be duplicate)\n"

        send_mail(subject, msg, from_email, to_email_list)
