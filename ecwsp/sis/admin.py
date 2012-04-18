from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType

from ajax_select import make_ajax_form
from ajax_select.fields import autoselect_fields_check_can_add
import sys
from reversion.admin import VersionAdmin

from ecwsp.sis.models import *
from ecwsp.sis.forms import *
from ecwsp.sis.views import *
from ecwsp.sis.helper_functions import ReadPermissionModelAdmin
from custom_field.custom_field import CustomFieldAdmin
from ecwsp.schedule.models import *

# Global actions
def promote_to_worker(modeladmin, request, queryset):
    for object in queryset:
        object.promote_to_worker()
        LogEntry.objects.log_action(
                    user_id         = request.user.pk, 
                    content_type_id = ContentType.objects.get_for_model(object).pk,
                    object_id       = object.pk,
                    object_repr     = unicode(object), 
                    action_flag     = CHANGE
                )
        

def graduate_and_create_alumni(modeladmin, request, queryset):
    i = 0
    for object in queryset:
        object.graduate_and_create_alumni()
        LogEntry.objects.log_action(
            user_id         = request.user.pk, 
            content_type_id = ContentType.objects.get_for_model(object).pk,
            object_id       = object.pk,
            object_repr     = unicode(object), 
            action_flag     = CHANGE
        )
        i += 1
    messages.success(request, "%s students were set as graduated, marked inactive, and if installed created in the alumni app." % (i,))

def mark_inactive(modeladmin, request, queryset):
    for object in queryset:
        object.inactive=True
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

class ASPHistoryInline(admin.TabularInline):
    model = ASPHistory
    extra = 0
    
class StudentCohortInline(admin.TabularInline):
    model = Student.cohorts.through
    extra = 0

class StudentECInline(admin.TabularInline):
    model = Student.emergency_contacts.through
    extra = 1

class MarkingPeriodInline(admin.StackedInline):
    model = MarkingPeriod
    extra = 0

class StudentCourseInline(admin.TabularInline):
    model = CourseEnrollment
    form = make_ajax_form(CourseEnrollment, {'course':'course','exclude_days':'day'})
    fields = ['course', 'attendance_note', 'exclude_days']
    extra = 0

admin.site.register(GradeLevel)

class StudentAdmin(VersionAdmin, ReadPermissionModelAdmin, CustomFieldAdmin):
    def changelist_view(self, request, extra_context=None):
        """override to hide inactive students by default"""
        try:
            test = request.META['HTTP_REFERER'].split(request.META['PATH_INFO'])
            if test and test[-1] and not test[-1].startswith('?') and not request.GET.has_key('inactive__exact') and not request.GET.has_key('id__in'):
                return HttpResponseRedirect("/admin/sis/student/?inactive__exact=0")
        except: pass # In case there is no referer
        return super(StudentAdmin,self).changelist_view(request, extra_context=extra_context)

    
    def lookup_allowed(self, lookup, *args, **kwargs):
        if lookup in ('id', 'id__in', 'year__id__exact'):
            return True
        return super(StudentAdmin, self).lookup_allowed(lookup, *args, **kwargs)
    
    def render_change_form(self, request, context, *args, **kwargs):
        try:
            if context['original'].pic:
                txt = '<img src="' + str(context['original'].pic.url_70x65) + '"/>'
                context['adminform'].form.fields['pic'].help_text += txt
        except:
            print >> sys.stderr, "Error in StudentAdmin render_change_form"
        
        return super(StudentAdmin, self).render_change_form(request, context,  *args, **kwargs)
    
    def change_view(self, request, object_id, extra_context=None):
        courses = Course.objects.filter(courseenrollment__user__id=object_id, marking_period__school_year__active_year=True).distinct()
        for course in courses:
            course.enroll = course.courseenrollment_set.get(user__id=object_id).id
        other_courses = Course.objects.filter(courseenrollment__user__id=object_id, marking_period__school_year__active_year=False).distinct()
        for course in other_courses:
            course.enroll = course.courseenrollment_set.get(user__id=object_id).id
        my_context = {
            'courses': courses,
            'other_courses': other_courses,
        }
        return super(StudentAdmin, self).change_view(request, object_id, extra_context=my_context)
        
    def get_form(self, request, obj=None, **kwargs):
        form = super(StudentAdmin,self).get_form(request,obj,**kwargs)
        
        autoselect_fields_check_can_add(StudentForm, self.model ,request.user)
        if not request.user.has_perm('sis.view_ssn_student'):
            self.exclude = ("ssn",)
        return form
    
    fieldsets = [
        (None, {'fields': [('lname', 'fname'), ('mname', 'inactive'), ('date_dismissed','reason_left'), 'username', 'grad_date', 'pic', 'alert', ('sex', 'bday'), 'year',('unique_id','ssn'),
            'family_preferred_language', 'alt_email', 'notes','emergency_contacts', 'siblings','individual_education_program',]}),
    ]
    change_list_template = "admin/sis/student/change_list.html"
    form = StudentForm
    search_fields = ['fname', 'lname', 'username', 'unique_id', 'street', 'state', 'zip', 'id']
    inlines = [StudentNumberInline, StudentCohortInline, StudentFileInline, StudentHealthRecordInline, TranscriptNoteInline, StudentAwardInline, ASPHistoryInline]
    actions = [promote_to_worker, mark_inactive, graduate_and_create_alumni]
    list_filter = ['inactive','year']
    list_display = ['__unicode__','year']
admin.site.register(Student, StudentAdmin)

### Second student admin just for courses
class StudentCourse(Student):
    class Meta:
        proxy = True
class StudentCourseAdmin(admin.ModelAdmin):
    inlines = [StudentCourseInline]
    search_fields = ['fname', 'lname', 'username', 'unique_id', 'street', 'state', 'zip', 'id']
    fields = ['fname', 'lname']
    list_filter = ['inactive','year']
    readonly_fields = fields
admin.site.register(StudentCourse, StudentCourseAdmin)

class EmergencyContactAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': [('lname', 'fname'), 'mname', ('relationship_to_student','email'), ('primary_contact', 'emergency_only')]}),
        ('Address', {'fields': ['street', ('city', 'state'), 'zip'],
            'classes': ['collapse']}),
    ]
    inlines = [EmergencyContactInline, StudentECInline]
    search_fields = ['fname', 'lname', 'email', 'student__fname', 'student__lname']
admin.site.register(EmergencyContact, EmergencyContactAdmin)

admin.site.register(MdlUser) # Not used?

admin.site.register(LanguageChoice)

class CohortAdmin(admin.ModelAdmin):
    form = CohortForm
    filter_horizontal = ('students',)
    
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

admin.site.register(ReasonLeft)
admin.site.register(ReportField)

admin.site.register(TranscriptNoteChoices)

class SchoolYearAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super(SchoolYearAdmin, self).get_form(request, obj, **kwargs)
        if not 'ecwsp.benchmark_grade' in settings.INSTALLED_APPS:
            self.exclude = ('benchmark_grade',)
        return form
    inlines = [MarkingPeriodInline]
admin.site.register(SchoolYear, SchoolYearAdmin)

class ImportLogAdmin(admin.ModelAdmin):
    list_display = ['user','date','errors']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
admin.site.register(ImportLog, ImportLogAdmin)