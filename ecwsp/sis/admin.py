from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.models import LogEntry, CHANGE
from django.forms import ValidationError

import sys
from reversion.admin import VersionAdmin

from ecwsp.sis.models import (Student, StudentNumber, EmergencyContactNumber, TranscriptNote,
        StudentFile, ClassYear, EmergencyContact, StudentHealthRecord, Faculty, GradeLevel,
        LanguageChoice, Cohort, PerCourseSectionCohort, ReasonLeft, TranscriptNoteChoices,
        SchoolYear, GradeScale, GradeScaleRule, MessageToStudent, FamilyAccessUser)
from ecwsp.schedule.models import AwardStudent, MarkingPeriod, CourseEnrollment, CourseSection
from custom_field.custom_field import CustomFieldAdmin
import autocomplete_light


def mark_inactive(modeladmin, request, queryset):
    for object in queryset:
        object.is_active=False
        LogEntry.objects.log_action(
                    user_id         = request.user.pk,
                    content_type_id = ContentType.objects.get_for_model(object).pk,
                    object_id       = object.pk,
                    object_repr     = unicode(object),
                    action_flag     = CHANGE
                )
        object.save()

class StudentNumberInline(admin.TabularInline):
    model = StudentNumber
    extra = 0


class EmergencyContactInline(admin.TabularInline):
    model = EmergencyContactNumber
    extra = 1
    classes = ('grp-collapse grp-open',)
    verbose_name = "Student Contact Number"
    verbose_name_plural = "Student Contact Numbers"
    from django.forms import TextInput, Textarea
    from django.db import models
    formfield_overrides = {
        models.CharField: {'widget': TextInput()},
    }

class TranscriptNoteInline(admin.TabularInline):
    model = TranscriptNote
    extra = 0

class StudentFileInline(admin.TabularInline):
    model = StudentFile
    extra = 0


class StudentHealthRecordInline(admin.TabularInline):
    model = StudentHealthRecord
    extra = 0

class StudentAwardInline(admin.TabularInline):
    model = AwardStudent
    extra = 0

class StudentCohortInline(admin.TabularInline):
    model = Student.cohorts.through
    form = autocomplete_light.modelform_factory(Student.cohorts.through)
    extra = 0

class StudentECInline(admin.TabularInline):
    model = Student.emergency_contacts.through
    extra = 0
    classes = ('grp-collapse grp-open',)
    verbose_name = "Student for Contact"
    verbose_name_plural = "Students for Contact"


class MarkingPeriodInline(admin.StackedInline):
    model = MarkingPeriod
    extra = 0
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


class FacultyAdmin(admin.ModelAdmin):
    fields = ['username', 'is_active', 'first_name', 'last_name', 'email', 'number', 'ext', 'teacher']
    search_fields = list_display = ['username', 'first_name', 'last_name', 'is_active']

admin.site.register(Faculty, FacultyAdmin)

class StudentCourseSectionInline(admin.TabularInline):
    model = CourseEnrollment
    form = autocomplete_light.modelform_factory(CourseEnrollment)
    fields = ('course_section', 'attendance_note')
    extra = 0
    classes = ('grp-collapse grp-closed',)

admin.site.register(GradeLevel)


class StudentAdmin(VersionAdmin, CustomFieldAdmin):
    def changelist_view(self, request, extra_context=None):
        """override to hide inactive students by default"""
        try:
            test = request.META['HTTP_REFERER'].split(request.META['PATH_INFO'])
            if test and test[-1] and not test[-1].startswith('?') and not request.GET.has_key('is_active__exact') and not request.GET.has_key('id__in'):
                return HttpResponseRedirect("/admin/sis/student/?is_active__exact=1")
        except: pass # In case there is no referer
        return super(StudentAdmin,self).changelist_view(request, extra_context=extra_context)


    def lookup_allowed(self, lookup, *args, **kwargs):
        if lookup in ('id', 'id__in', 'year__id__exact'):
            return True
        return super(StudentAdmin, self).lookup_allowed(lookup, *args, **kwargs)

    def render_change_form(self, request, context, *args, **kwargs):
        if 'original' in context and context['original'] is not None:
            if context['original'].alert:
                messages.add_message(request, messages.INFO, 'ALERT: {0}'.format(context["original"].alert))
            for record in context['original'].studenthealthrecord_set.all():
                messages.add_message(request, messages.INFO, 'HEALTH RECORD: {0}'.format(record.record))
            try:
                if context['original'].pic:
                    txt = '<img src="' + str(context['original'].pic.url_70x65) + '"/>'
                    context['adminform'].form.fields['pic'].help_text += txt
            except:
                print >> sys.stderr, "Error in StudentAdmin render_change_form"

        if 'ecwsp.benchmark_grade' in settings.INSTALLED_APPS:
            context['adminform'].form.fields['family_access_users'].queryset = User.objects.filter(groups__name='family')

        return super(StudentAdmin, self).render_change_form(request, context,  *args, **kwargs)

    def save_model(self, request, obj, form, change):
        super(StudentAdmin, self).save_model(request, obj, form, change)
        form.save_m2m()
        if 'ecwsp.benchmark_grade' in settings.INSTALLED_APPS:
            group = Group.objects.get_or_create(name='family')[0]
            for user in obj.family_access_users.all():
                user.groups.add(group)
                user.save()


    def get_form(self, request, obj=None, **kwargs):
        exclude = []
        if not request.user.has_perm('sis.view_ssn_student'):
            exclude.append('ssn')
        if not 'ecwsp.benchmark_grade' in settings.INSTALLED_APPS:
            exclude.append('family_access_users')
        if len(exclude):
            kwargs['exclude'] = exclude
        return super(StudentAdmin,self).get_form(request,obj,**kwargs)

    def get_fieldsets(self, request, obj=None):
        ssn = request.user.has_perm('sis.view_ssn_student')
        family_access_users = 'ecwsp.benchmark_grade' in settings.INSTALLED_APPS
        return ((
            None,
            {
                'fields': (
                    ('last_name', 'first_name'),
                    ('mname', 'is_active'),
                    ('username', 'email'),
                    ('date_dismissed', 'reason_left'),
                    'grad_date',
                    'pic',
                    'alert',
                    ('sex', 'bday'),
                    ('class_of_year', 'year'),
                    ('unique_id', 'ssn') if ssn else 'unique_id',
                    'family_preferred_language',
                    'alt_email',
                    'notes',
                    'emergency_contacts',
                    'siblings',
                    'individual_education_program',
                    # `None` does not work well! Use an empty tuple instead.
                    'family_access_users' if family_access_users else tuple(),
                )
            }
        ),)

    change_list_template = "admin/sis/student/change_list.html"
    form = autocomplete_light.modelform_factory(Student)
    readonly_fields = ['year']
    search_fields = ['first_name', 'last_name', 'username', 'unique_id', 'street', 'state', 'zip', 'id', 'studentnumber__number']
    inlines = [StudentCourseSectionInline, StudentNumberInline, StudentCohortInline, StudentFileInline, StudentHealthRecordInline, TranscriptNoteInline, StudentAwardInline]
    actions = [mark_inactive]
    list_filter = ['is_active', 'year', 'class_of_year']
    list_display = ['first_name','last_name','year','is_active','primary_cohort', 'phone', 'gpa']
    if 'ecwsp.benchmark_grade' in settings.INSTALLED_APPS:
        filter_horizontal = ('family_access_users',)

admin.site.register(Student, StudentAdmin)
admin.site.register(ClassYear)

### Second student admin just for courses
class StudentCourseSection(Student):
    class Meta:
        proxy = True
class StudentCourseSectionAdmin(admin.ModelAdmin):
    inlines = [StudentCourseSectionInline]
    search_fields = ['first_name', 'last_name', 'username', 'unique_id', 'street', 'state', 'zip', 'id']
    fields = ['first_name', 'last_name']
    list_filter = ['is_active','year']
    readonly_fields = fields
admin.site.register(StudentCourseSection, StudentCourseSectionAdmin)



class EmergencyContactAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': [('lname', 'fname'), 'mname', ('relationship_to_student','email'), 'primary_contact', 'emergency_only',]}),
        ('Address', {'fields': ['street', ('city', 'state',), 'zip'],
            'classes': ['collapse']}),
    ]
    if 'ecwsp.integrations.schoolreach' in settings.INSTALLED_APPS:
        fieldsets[0][1]['fields'].append('sync_schoolreach')
    list_filter = ['primary_contact',]
    inlines = [EmergencyContactInline, StudentECInline]
    search_fields = ['fname', 'lname', 'email', 'student__first_name', 'student__last_name']
    list_display = ['fname', 'lname', 'primary_contact', 'relationship_to_student', 'show_student']

admin.site.register(EmergencyContact, EmergencyContactAdmin)

admin.site.register(LanguageChoice)

class CohortAdmin(admin.ModelAdmin):
    inlines = (StudentCohortInline,)

    def queryset(self, request):
        # exclude PerCourseSectionCohorts from Cohort admin
        qs = super(CohortAdmin, self).queryset(request)
        return qs.filter(percoursesectioncohort=None)

    def save_model(self, request, obj, form, change):
        if obj.id:
            prev_students = Cohort.objects.get(id=obj.id).students.all()
        else:
            prev_students = Student.objects.none()

        # Django is retarded about querysets,
        # save these ids because the queryset will just change later
        student_ids = []
        for student in prev_students:
            student_ids.append(student.id)

        super(CohortAdmin, self).save_model(request, obj, form, change)
        form.save_m2m()

        for student in obj.students.all() | Student.objects.filter(id__in=student_ids):
            student.cache_cohorts()
            student.save()

admin.site.register(Cohort, CohortAdmin)

class PerCourseSectionCohortAdmin(CohortAdmin):
    exclude = ('primary',)

    def __get_teacher_courses(self, username):
        from django.db.models import Q
        from ecwsp.schedule.models import CourseSection
        try:
            teacher = Faculty.objects.get(username=username)
            teacher_courses = CourseSection.objects.filter(teachers=teacher).distinct()
        except:
            teacher_courses = []
            #TODO: Clean this! I guess it was to flag DB inconsistencies
            import traceback
            print traceback.format_exc()
        return teacher_courses

    def queryset(self, request):
        qs = super(CohortAdmin, self).queryset(request)
        if request.user.is_superuser or request.user.groups.filter(name='registrar').count():
            return qs
        return qs.filter(course_section__in=self.__get_teacher_courses(request.user.username))

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        # TODO: use a wizard or something and filter by THIS COHORT'S COURSE instead of all the teacher's courses
        if db_field.name == 'students':
            if not request.user.is_superuser and not request.user.groups.filter(name='registrar').count():
                kwargs['queryset'] = Student.objects.filter(coursesection__in=self.__get_teacher_courses(request.user.username))
        return super(PerCourseSectionCohortAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)


admin.site.register(PerCourseSectionCohort, PerCourseSectionCohortAdmin)

admin.site.register(ReasonLeft)

admin.site.register(TranscriptNoteChoices)

class SchoolYearAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'active_year')
    def get_form(self, request, obj=None, **kwargs):
        form = super(SchoolYearAdmin, self).get_form(request, obj, **kwargs)
        if not 'ecwsp.benchmark_grade' in settings.INSTALLED_APPS:
            self.exclude = ('benchmark_grade',)
        return form
    inlines = [MarkingPeriodInline]
admin.site.register(SchoolYear, SchoolYearAdmin)

class GradeScaleRuleInline(admin.TabularInline):
    model = GradeScaleRule

class GradeScaleAdmin(admin.ModelAdmin):
    inlines = [GradeScaleRuleInline]
admin.site.register(GradeScale, GradeScaleAdmin)


admin.site.register(MessageToStudent)

from django.contrib.auth.admin import UserAdmin
class FamilyAccessUserAdmin(UserAdmin,admin.ModelAdmin):
    fields = ('is_active','username','first_name','last_name','password')
    fieldsets = None
    list_display = ('username','first_name','last_name','is_active',)
#    list_filter = ('is_active','workteam')
    def queryset(self,request):
        return User.objects.filter(groups__name='family')
if 'ecwsp.benchmark_grade' in settings.INSTALLED_APPS:
    admin.site.register(FamilyAccessUser,FamilyAccessUserAdmin)

class UserForm(UserChangeForm):
    """ Extended User form to provide extra validation """
    class Meta:
        model = User

    def clean(self):
        super(UserForm, self).clean()
        groups = self.cleaned_data.get(
             'groups', None).all()
        student_group = Group.objects.get_or_create(name="students")[0]
        teacher_group = Group.objects.get_or_create(name="teacher")[0]
        if student_group in groups and teacher_group in groups:
            message = "User cannot be both a teacher and a student"
            raise ValidationError(message)
        return self.cleaned_data

class UserAdmin(UserAdmin):
    form = UserForm

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
