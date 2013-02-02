#       models.py
#       
#       Copyright 2010 Cristo Rey New York High School
#        Author David M Burke <david@burkesoftware.com>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

from django.db import models
from django.contrib import messages
from django.contrib.auth.models import User
from django.conf import settings
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
    name = models.CharField(max_length=100)
    value = models.TextField(blank=True)
    file = models.FileField(blank=True, null=True, upload_to="configuration", help_text="Some configuration options are for file uploads")
    help_text = models.TextField(blank=True)
    
    default_configs = {
        'letter_grade_required_for_pass': ('60', 'Minimum grade required to be considered "passing"'),
        'school pay rate per hour': ('13.00', ''),
        'From Email Address': ('donotreply@cristoreyny.org', ''),
        'work_study show commment default': ('True', ''),
        'work_study_timesheet_initial_time': ('True', ''),
        'work_study_contract_from_address': ('donotreply@cristoreyny.org', ''),
        'work_study_contract_cc_address': ('', ''),
        'Students per FTE': ('.2', ''),
        'S': ('5', 'David is an idiot who can not code'),
        'Edit all Student Worker Fields': ('False', ''),
        'sync sugarcrm minutes': ('30', ''),
        'counseling_referral_notice_email_to': ('', ''),
        'Admissions to student also makes student worker': ('False', ''),
        'admissions_override_year_start': ('', 'Must be ISO date (ex 2012-10-25) or blank'),
        'Pasing Grade': ('70', ''),
        'Letter Passing Grade': ('A,B,C,P', ''),
        'Only Active Classes in Schedule': ('', ''),
        'attendance_create_work_attendance': ('False', ''),
        'Default City': ('', ''),
        'How to obtain student email': ('append','append, user, or student', ''),
        'email': ('@change.me', ''),
        'Clear Placement for Inactive Students': ('False', ''),
        'Benchmark-based grading': ('False', ''),
        'School Name': ('Unnamed School', ''),
        'School Color': ('', ''),
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
    
        
class Template(models.Model):
    name = models.CharField(max_length=100, unique=True)
    file = models.FileField(upload_to="templates")
    general_student = models.BooleanField(help_text="Can be used on student reports")
    report_card = models.BooleanField(help_text="Can be used on grade reports, gathers data for one year")
    transcript = models.BooleanField(help_text="Can be used on grade reports, gathers data for all years")
    
    def __unicode__(self):
        return self.name
    
    def get_template(self, request):
        """ Get template or return False with error message. """
        if self.file:
            return self.file
        messages.error(request, 'Template %s not found!' % (self.name,))
        return False
    
    def get_template_path(self, request):
        """ Get template file path, or return False with error message. """
        if self.file:
            return self.file.path
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
        
