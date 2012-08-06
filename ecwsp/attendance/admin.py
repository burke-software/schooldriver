#   Copyright 2012 Burke Software and Consulting LLC
#   Author David M Burke <david@burkesoftware.com>
#   
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 3 of the License, or
#   (at your option) any later version.
#     
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#      
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#   MA 02110-1301, USA.

from django.contrib import admin
from django.contrib import messages
from django import forms
from daterange_filter import filter #https://github.com/tzulberti/django-datefilterspec

from models import *

from ajax_select import make_ajax_form

class StudentAttendanceAdmin(admin.ModelAdmin):
    form = make_ajax_form(StudentAttendance, dict(student='attendance_quick_view_student'))
    list_display = ['student', 'date', 'status', 'notes', 'time']
    list_filter = ['date', 'status']
    list_editable = ['status', 'notes']
    search_fields = ['student__fname', 'student__lname', 'notes', 'status__name']
    def save_model(self, request, obj, form, change):
        #HACK to work around bug 13091
        try:
            obj.full_clean()
            obj.save()
        except forms.ValidationError:
            messages.warning(request, 'Could not save %s' % (obj,))
    
    def lookup_allowed(self, lookup, *args, **kwargs):
        if lookup in ('student','student__id__exact',):
            return True
        return super(StudentAttendanceAdmin, self).lookup_allowed(lookup, *args, **kwargs)
        
admin.site.register(StudentAttendance, StudentAttendanceAdmin)

admin.site.register(AttendanceLog)

class AttendanceStatusAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'excused', 'absent', 'tardy']
admin.site.register(AttendanceStatus,AttendanceStatusAdmin)
