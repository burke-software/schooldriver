from django.contrib import admin
from django.contrib import messages
from django import forms
from daterange_filter.filter import DateRangeFilter

from ecwsp.attendance.models import StudentAttendance, CourseSectionAttendance, AttendanceLog, AttendanceStatus

import autocomplete_light

class StudentAttendanceAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(StudentAttendance)
    list_display = ['student', 'date', 'status', 'notes', 'time']
    list_filter = [
        ('date', DateRangeFilter),
        'status'
        ]
    search_fields = ['student__first_name', 'student__last_name', 'notes', 'status__name']
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

class CourseSectionAttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'date', 'course_section', 'period', 'course_period', 'status', 'notes']
    list_filter = [
        ('date', DateRangeFilter),
        'status',
        'period'
        ]
    search_fields = ['student__first_name', 'student__last_name', 'notes', 'status__name']

    def lookup_allowed(self, lookup, *args, **kwargs):
        if lookup in ('student','student__id__exact',):
            return True
        return super(CourseSectionAttendanceAdmin, self).lookup_allowed(lookup, *args, **kwargs)
admin.site.register(CourseSectionAttendance, CourseSectionAttendanceAdmin)

admin.site.register(AttendanceLog)

class AttendanceStatusAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'excused', 'absent', 'tardy', 'half']
admin.site.register(AttendanceStatus,AttendanceStatusAdmin)
