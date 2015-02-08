from django import forms
from django.contrib import admin
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core import urlresolvers
from django.utils.safestring import mark_safe
from django.http import HttpResponseRedirect

from daterange_filter.filter import DateRangeFilter

from ecwsp.sis.models import Faculty, Student
from ecwsp.schedule.models import (CourseMeet, Course, Department, CourseEnrollment, MarkingPeriod,
    Period, Location, OmitCourseGPA, OmitYearGPA, Award, CourseSectionTeacher,
    DepartmentGraduationCredits, DaysOff, CourseSection, CourseType, ISOWEEKDAY_TO_VERBOSE)
import reversion

def copy(modeladmin, request, queryset):
    for object in queryset:
        object.copy_instance(request)

class CourseMeetInline(admin.TabularInline):
    model = CourseMeet
    extra = 1

class CourseSectionInline(admin.StackedInline):
    model = CourseSection
    extra = 0
    readonly_fields = ['course_section_link']
    fields = ['course_section_link', 'name', 'is_active', 'marking_period', 'cohorts']

    def course_section_link(self, obj):
        change_url = urlresolvers.reverse('admin:schedule_coursesection_change', args=(obj.id,))
        return mark_safe('<a href="%s">%s</a>' % (change_url, obj))
    course_section_link.short_description = 'Course Section Link'

class CourseAdmin(reversion.VersionAdmin):
    list_display = ['fullname', 'department', 'credits', 'graded', 'is_active']
    search_fields = ['fullname', 'shortname', 'description', 'sections__teachers__username']
    list_filter = ['level', 'is_active', 'graded', 'homeroom', 'department']
    inlines = [CourseSectionInline]

    def save_model(self, request, obj, form, change):
        """Override save_model because django doesn't have a better way to access m2m fields"""
        obj.save()
        form.save_m2m()
        obj.save()

admin.site.register(Course, CourseAdmin)
admin.site.register(CourseType)

class CourseEnrollmentInline(admin.TabularInline):
    model = CourseEnrollment
    fields = ['user', 'attendance_note']
    readonly_fields = ['user']
    def has_add_permission(self, request):
        return False

class CourseSectionTeacherInline(admin.TabularInline):
    model = CourseSectionTeacher
    extra = 0

class CourseSectionAdmin(reversion.VersionAdmin):
    inlines = [CourseMeetInline, CourseSectionTeacherInline, CourseEnrollmentInline]
    list_display = ['name', 'grades_link', 'course', 'is_active']
    list_filter = ['course__level', 'course__department', 'teachers']
    search_fields = ['name', 'course__fullname', 'teachers__username']
    readonly_fields = ['course_link']
    fields = ['course', 'course_link', 'name', 'is_active', 'marking_period', 'cohorts']
    actions = [copy]

    def course_link(self, obj):
        change_url = urlresolvers.reverse('admin:schedule_course_change', args=(obj.course.id,))
        return mark_safe('<a href="%s">%s</a>' % (change_url, obj.course))
    course_link.short_description = 'Course Link'

    def save_related(self, request, form, formsets, change):
        super(CourseSectionAdmin, self).save_related(
            request, form, formsets, change
        )
        form.instance.populate_all_grades()

admin.site.register(CourseSection, CourseSectionAdmin)


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


class CourseEnrollmentForm(forms.ModelForm):
    model = CourseEnrollment
    exclude_days = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(), choices=ISOWEEKDAY_TO_VERBOSE)


class CourseEnrollmentAdmin(admin.ModelAdmin):
    form = CourseEnrollmentForm
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
