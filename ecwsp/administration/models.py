from django.db import models
from django.contrib import messages
from django.contrib.auth.models import User
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files import File
from datetime import datetime
import httpagentparser
import urllib
import os

from ecwsp.sis.helper_functions import Callable

class AccessLog(models.Model):
    login = models.ForeignKey(User)
    ua = models.CharField(max_length=2000, help_text="User agent. We can use this to determine operating system and browser in use.")
    date = models.DateTimeField(default=datetime.now)
    ip = models.IPAddressField()
    usage = models.CharField(max_length=255)
    def __unicode__(self):
        return unicode(self.login) + " " + unicode(self.usage) + " " + unicode(self.date);
    def os(self):
        try:
            return httpagentparser.simple_detect(self.ua)[0]
        except:
            return "Unknown"
    def browser(self):
        try:
            return httpagentparser.simple_detect(self.ua)[1]
        except:
            return "Unknown"

class Configuration(models.Model):
    name = models.CharField(max_length=100, unique=True)
    value = models.TextField(blank=True)
    file = models.FileField(blank=True, null=True, upload_to="configuration", help_text="Some configuration options are for file uploads")
    help_text = models.TextField(blank=True)

    default_configs = {
        'school pay rate per hour': ('13.00', ''),
        'From Email Address': ('donotreply@cristoreyny.org', ''),
        'work_study show commment default': ('True', ''),
        'work_study_timesheet_initial_time': ('True', ''),
        'work_study_contract_from_address': ('donotreply@cristoreyny.org', ''),
        'work_study_contract_cc_address': ('', ''),
        'Students per FTE': ('.2', ''),
        'S': ('5', 'David is an idiot who can not code'),
        'Edit all Student Worker Fields': ('False', ''),
        'counseling_referral_notice_email_to': ('', ''),
        'Admissions to student also makes student worker': ('False', ''),
        'admissions_override_year_start': ('', 'Must be ISO date (ex 2012-10-25) or blank'),
        'Passing Grade': ('70', ''),
        'Letter Passing Grade': ('A,B,C,P', ''),
        'Only Active Classes in Schedule': ('', ''),
        'Hide Empty Periods in Schedule': ('False', ''),
        'attendance_create_work_attendance': ('False', ''),
        'Default City': ('', ''),
        'How to obtain student email': ('append','append, user, or student', ''),
        'email': ('@change.me', ''),
        'Clear Placement for Inactive Students': ('False', ''),
        'Benchmark-based grading': ('False', ''),
        'Volunteer Track Required Hours': ('20', ''),
        'Volunteer Track Manager Emails': ('', ''),
        'attendance_disc_tardies_before_disc': ('1', ''),
        'attendance_disc_infraction': ('', ''),
        'attendance_disc_action': ('', ''),
        'Discipline Merit Default Days': ('14', ''),
        'Discipline Merit Level One': ('0', ''),
        'Discipline Merit Level Two': ('1', ''),
        'Discipline Merit Level Three': ('3', ''),
        'Discipline Merit Level Four': ('5', ''),
        'work_study message to student missing time sheet': ('You did not submit a timesheet today.', ''),
        'admissions_inquiry_form_css': ('', 'CSS for Inquiry Form'),
        'admissions_notify_email': ('', 'Send admissions notifications to this email. Comma separated are ok.'),
        'admissions_hide_inquiry_grade': ('', 'IDs of grade (fresh, soph, etc) to exclude on inquiry form. Comma separated are ok.'),
        'grades_allow_spreadsheet_import': ('True', 'Allow users to import a spreadsheet to submit grades'),
        'Grade comment length limit': ('500', 'Maximum number of characters allowed in grade comments; values above 500 ignored'),
        'Gradebook extra information': ('averages', "Set to 'averages' to see the class average for each assignment. \
Use 'demonstrations' to see counts of demonstrations for students and assignments."),
        'Gradebook hide fields': ('', "Separate with commas. Options include: marking_period, assignment_type, benchmark, date, description."),
        'Default course credits': (1, "This number will appear in the 'Credits' field when creating new courses."),
    }

    def __unicode__(self):
        return self.name

    def get_or_default(name, default=None, help_text=None):
        """ Get the config object or create it with a default. Always use this when gettings configs
        Defaults are hard coded into this python file, you must add new values here for new configs!
        default paramater is legacy and does not do anything
        """
        object, created = Configuration.objects.get_or_create(name=name)
        if created:
            default_config = Configuration.default_configs[name]
            object.value = default_config[0]
            object.help_text = default_config[1]
            object.save()
        return object
    get_or_default = Callable(get_or_default)


def validate_file_extension(value):
    if not value.name[-4:] in ['.odt', '.ods']:
        raise ValidationError('Template must be odt or ods file.')

class Template(models.Model):
    name = models.CharField(max_length=100, unique=True)
    file = models.FileField(upload_to="templates", validators=[validate_file_extension])
    general_student = models.BooleanField(default=False, help_text="Can be used on student reports")
    report_card = models.BooleanField(default=False, help_text="Can be used on grade reports, gathers data for one year")
    benchmark_report_card = models.BooleanField(default=False, help_text="A highly detailed, single-year report card for benchmark-based grading")
    transcript = models.BooleanField(default=False, help_text="Can be used on grade reports, gathers data for all years")

    def __unicode__(self):
        text = self.name
        if self.report_card:
            text += ' (report card)'
        if self.transcript:
            text += ' (transcript)'
        return text

    def get_template(self, request):
        """ Get template or return False with error message. """
        if self.file:
            return self.file
        messages.error(request, 'Template %s not found!' % (self.name,))
        return False

    def get_template_path(self, request):
        """ Get template file path, or return False with error message. """
        if self.file:
            return self.file
        messages.error(request, 'Template %s not found!' % (self.name,))
        return False

    def get_or_make_blank(name):
        """ Get a template. If it doesn't exist create one that will be a blank document to prevent errors """
        template, created = Template.objects.get_or_create(name=name)
        if not template.file:
            result = settings.MEDIA_ROOT + 'blank.odt'
            template.file.save(
                'blank.odt',
                File(open(result))
                )
            template.save()
        return template
    get_or_make_blank = Callable(get_or_make_blank)

