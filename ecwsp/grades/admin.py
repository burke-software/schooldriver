from django.contrib import admin

from models import *

admin.site.register(GradeComment)

class GradeAdmin(admin.ModelAdmin):
    list_display = ['grade', 'course', 'student', 'marking_period', 'override_final']
    list_filter = ['date', 'override_final']
    search_fields = ['student__first_name', 'student__last_name', 'course__fullname', 'course__shortname']
admin.site.register(Grade, GradeAdmin)
