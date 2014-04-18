from django.contrib import admin
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect

from ajax_select import make_ajax_form
from ajax_select.fields import autoselect_fields_check_can_add
from daterange_filter.filter import DateRangeFilter

from ecwsp.sis.models import Faculty, Student
from ecwsp.schedule.models import CourseMeet, Course, Department, CourseEnrollment, MarkingPeriod
from ecwsp.schedule.models import Period, Location, OmitCourseGPA, OmitYearGPA, Award
from ecwsp.schedule.models import DepartmentGraduationCredits, DaysOff, Day, CourseSection

def copy(modeladmin, request, queryset):
    for object in queryset:
        object.copy_instance(request)

class CourseMeetInline(admin.TabularInline):
    model = CourseMeet
    extra = 1
    
class CourseSectionInline(admin.StackedInline):
    model = CourseSection
    extra = 0

class CourseAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'grades_link']
    search_fields = ['fullname', 'shortname', 'description', 'teacher__username']
    list_filter = ['level', 'is_active', 'graded', 'homeroom']
    inlines = [CourseSectionInline]
    
    def save_model(self, request, obj, form, change):
        """Override save_model because django doesn't have a better way to access m2m fields"""
        obj.save()
        form.save_m2m()
        obj.save()
        
    
admin.site.register(Course, CourseAdmin)

class DepartmentGraduationCreditsInline(admin.TabularInline):
    model = DepartmentGraduationCredits
    verbose_name = 'graduation credits requirement'
    verbose_name_plural = 'graduation credits requirements'
    extra = 1

class DepartmentAdmin(admin.ModelAdmin):
    inlines = [DepartmentGraduationCreditsInline]

admin.site.register(Department, DepartmentAdmin)

class DaysOffInline(admin.TabularInline):
    model = DaysOff
    extra = 1
    
admin.site.register(Day)
    
class CourseEnrollmentAdmin(admin.ModelAdmin):
    search_fields = ['user__username', 'user__first_name',]
    list_display = ['user', 'attendance_note']
admin.site.register(CourseEnrollment, CourseEnrollmentAdmin)

class MarkingPeriodAdmin(admin.ModelAdmin):
    inlines = [DaysOffInline]
    fieldsets = (
        ('', {
            'fields': ('active','name','shortname',('start_date','end_date'),
                       'grades_due','school_year','show_reports',
                       'school_days','weight'),
        },),
        ('Change active days', {
            'classes': ('grp-collapse grp-closed',),
            'fields': ('monday','tuesday','wednesday','thursday',
                       'friday','saturday','sunday',),
        },),
    )
admin.site.register(MarkingPeriod, MarkingPeriodAdmin)

admin.site.register(Period)

admin.site.register(Location)

admin.site.register(OmitCourseGPA)

admin.site.register(OmitYearGPA)

admin.site.register(Award)
