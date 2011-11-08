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
from datetime import datetime
import httpagentparser

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
    
    def __unicode__(self):
        return self.name
    
    def get_or_default(name, default=None):
        """ Get the config object or create it with a default. Always use this when gettings configs"""
        object, created = Configuration.objects.get_or_create(name=name)
        if created:
            object.value = default
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
    
    def get_template_path(self, request):
        """ Get template file path, or return False with error message. """
        if self.file:
            return self.file.path
        messages.error(request, 'Template %s not found!' % (self.name,))
        return False
