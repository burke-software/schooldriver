from django.contrib import admin

from .models import GradeComment, Grade

admin.site.register(GradeComment)

class GradeAdmin(admin.ModelAdmin):
    list_display = ['grade', 'course_section', 'student', 'marking_period', 'override_final']
    list_filter = ['date', 'override_final']
    search_fields = ['student__first_name', 'student__last_name', 'course_section__course__fullname', 'course_section__course__shortname']
admin.site.register(Grade, GradeAdmin)


