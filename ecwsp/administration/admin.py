#       admin.py
#       
#       Copyright 2010 Cristo Rey New York High School
#       Author David M Burke <david@burkesoftware.com>
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

from django.contrib import admin
from django.contrib.admin.models import LogEntry

from ecwsp.administration.models import *
from ecwsp.administration.forms import *

class ConfigurationAdmin(admin.ModelAdmin):
    search_fields = ['name']

admin.site.register(Configuration, ConfigurationAdmin)

class AccessLogAdmin(admin.ModelAdmin):
    list_display = ('login', 'usage', 'date', 'os', 'browser')
    search_fields = ['login__username', 'login__first_name',]
admin.site.register(AccessLog, AccessLogAdmin)

class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'action_time', 'content_type', 'object_repr', 'is_addition', 'is_deletion', 'is_change')
    list_filter = ('action_flag', 'action_time')
    search_fields = ['user__username', 'content_type__name', 'object_repr']
    readonly_fields = ('user', 'action_time', 'content_type', 'object_repr', 'action_flag', 'object_id', 'change_message', 'action_time')
admin.site.register(LogEntry, LogEntryAdmin)

class TemplateAdmin(admin.ModelAdmin):
    form = TemplateForm
admin.site.register(Template, TemplateAdmin)

