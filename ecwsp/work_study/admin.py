from django import forms
from django.http import HttpResponseRedirect
from django.contrib import admin
from django.utils.encoding import smart_unicode
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.core.urlresolvers import reverse
from daterange_filter.filter import DateRangeFilter

from .models import (CompContract, CompanyHistory, Company, WorkTeam, CraContact,
        PickupLocation, WorkTeamUser, StudentWorker, StudentWorkerRoute, PresetComment, 
        StudentInteraction, Contact, TimeSheetPerformanceChoice, TimeSheet, Attendance,
        AttendanceFee, AttendanceReason, Personality, ClientVisit, Survey, PaymentOption,
        StudentDesiredSkill, StudentFunctionalResponsibility, MessageToSupervisor)
from ecwsp.sis.models import StudentNumber
from ecwsp.sis.admin import StudentFileInline
from reversion.admin import VersionAdmin
from ecwsp.administration.models import Configuration
from django.contrib.auth.models import User
from django.db.models import Q
from custom_field.custom_field import CustomFieldAdmin
import autocomplete_light

import logging
    
class StudentNumberInline(admin.TabularInline):
    model = StudentNumber
    extra = 1    
    
class CompContractInline(admin.TabularInline):
    model = CompContract
    extra = 0
    fields = ('contract_file', 'date', 'school_year', 'number_students', 'signed')

class CompanyHistoryInline(admin.TabularInline):
    model = CompanyHistory
    extra = 0
    max_num = 0
    readonly_fields = ['placement']

class CompanyAdmin(admin.ModelAdmin):
    def render_change_form(self, request, context, *args, **kwargs):
        if 'original' in context and context['original']:
            workteams = WorkTeam.objects.filter(company=context['original'].id)
            txt = "<h5>Work teams:</h5>"
            for workteam in workteams:
                txt += "<a href=\"/admin/work_study/workteam/" + \
                    unicode(workteam.id) + "\" target=\"_blank\">" + unicode(workteam) + \
                    "</a><br/>"
            txt += "<h5>Current Students</h5>"
            students = StudentWorker.objects.filter(placement__company=context['original'].id)
            for student in students:
                txt += u'<a href="/admin/work_study/studentworker/%s/" target="_blank"/> %s </a></br>' % (student.id, student,)
            txt += "<h5>Past Students</h5>"
            histories = CompanyHistory.objects.filter(placement__company=context['original'].id)
            for history in histories:
                txt += '%s </br>' % (unicode(history),)
            txt += "<h5>Eletronic contract link:</h5>"
            txt += '<a href="{0}">{0}</a>'.format(settings.BASE_URL + reverse('ecwsp.work_study.views.company_contract1', args=(context['original'].id,)))
            context['adminform'].form.fields['name'].help_text = txt
        return super(CompanyAdmin, self).render_change_form(request, context, args, kwargs)
    search_fields = ('workteam__studentworker__first_name', 'workteam__studentworker__last_name', 'workteam__team_name')
    list_display = ('name','fte')
    inlines = [CompContractInline]
admin.site.register(Company, CompanyAdmin)


class MapImageWidget(forms.CheckboxInput):
    def render(self, name, value, attrs=None):
        output = []
        output.append(super(MapImageWidget, self).render(name, value, attrs))
        output.append("If checked, the above map file will be overwritten with Google Maps. <table><tr><td><a href=\"javascript:get_map()\">Preview Google Maps</a></td></tr><tr><td> <img width=\"400px\" height=\"400px\" name=\"mapframe\"></iframe> </td></tr></table>")
        return mark_safe(u''.join(output))
        
            
class WorkTeamForm(forms.ModelForm):
    class Meta:
        model = WorkTeam
    
    use_google_maps = forms.BooleanField(required=False, widget=MapImageWidget)


class WorkTeamAdmin(VersionAdmin, CustomFieldAdmin):
    form = WorkTeamForm
    
    def changelist_view(self, request, extra_context=None):
        """override to hide inactive workteams by default"""
        try:
            test = request.META['HTTP_REFERER'].split(request.META['PATH_INFO'])
            if test and test[-1] and not test[-1].startswith('?') and not request.GET.has_key('inactive__exact') and not request.GET.has_key('id__in'):
                return HttpResponseRedirect("/admin/work_study/workteam/?inactive__exact=0")
        except: pass # In case there is no referer
        return super(WorkTeamAdmin,self).changelist_view(request, extra_context=extra_context)
    
    def render_change_form(self, request, context, *args, **kwargs):
        # only show login in group company    
        compUsers = User.objects.filter(Q(groups__name='company'))
        context['adminform'].form.fields['login'].queryset = compUsers
        try:
            students = StudentWorker.objects.filter(placement=context['original'].id)
            txt = "<h5>Students working here</h5>"
            for stu in students:
                txt += unicode(stu.edit_link() + '<br/>')
            txt += "<br/><br/><a href=\"/admin/work_study/timesheet/?company__id__exact=%s\" target=\"_blank\">Timesheets for company</a>" % \
                (context['original'].id) 
            txt += "<br/><a href=\"/admin/work_study/survey/?q=%s\" target=\"_blank\">Surveys for this company</a>" % \
                (context['original'].team_name)
            context['adminform'].form.fields['team_name'].help_text = txt
        except:
            print >> sys.stderr, "KeyError at /admin/work_study/company/add/  original"
        return super(WorkTeamAdmin, self).render_change_form(request, context, args, kwargs)
    
    def save_model(self, request, obj, form, change):
        super(WorkTeamAdmin, self).save_model(request, obj, form, change)
        form.save_m2m()
        group = Group.objects.get_or_create(name="company")[0]
        for user in obj.login.all():
            user.groups.add(group)
            user.save()
    
    search_fields = ['company__name', 'team_name', 'address',]
    list_filter = ['inactive', 'pm_transport_group', 'travel_route', 'industry_type', 'paying','cras']
    fieldsets = [
        (None, {'fields': [('company', 'inactive'), 'team_name', 'job_description', 'company_description', 'login', ('paying', 'funded_by'), 'industry_type', 'cras', ('am_transport_group', 'pm_transport_group'), 'contacts']}),
        ("Location", {'fields': ['address', ('city', 'state'), 'zip',('travel_route', 'stop_location'), ('map', 'use_google_maps'), 'directions_to', 'directions_pickup', ('time_earliest', 'time_latest', 'time_ideal')], 'classes': ['collapse']}),
    ]
    filter_horizontal = ('contacts', 'login')
    list_display = ('team_name', 'company', 'stop_location', 'am_transport_group', 'fte', 'paying', 'cra')
admin.site.register(WorkTeam, WorkTeamAdmin)

class CraContactAdmin(admin.ModelAdmin):
    search_fields = ['name__username', 'name__first_name', 'name__last_name']
admin.site.register(CraContact, CraContactAdmin)

class pickUpLocationAdmin(admin.ModelAdmin):
    search_fields = ['location']
admin.site.register(PickupLocation, pickUpLocationAdmin)

def increaseGradeLevel(modeladmin, request, queryset):
    for obj in queryset:
        obj.year = obj.year + 1
        obj.save()
increaseGradeLevel.shortDescription = "Increase grade level of selected students"
    
def approve(modeladmin, request, queryset):
    queryset.update(approved = True)
    for object in queryset:
        LogEntry.objects.log_action(
                    user_id         = request.user.pk, 
                    content_type_id = ContentType.objects.get_for_model(object).pk,
                    object_id       = object.pk,
                    object_repr     = unicode(object), 
                    action_flag     = CHANGE
                )
    
def move_to_former_students(modeladmin, request, queryset):
    for object in queryset:
        object.delete()

from django.contrib.auth.admin import UserAdmin
class WorkStudyUserAdmin(UserAdmin,admin.ModelAdmin):
    fields = ('is_active','username','first_name','last_name','password')
    fieldsets = None
    list_display = ('username','first_name','last_name','is_active',)
    list_filter = ('is_active','workteam')
    def queryset(self,request):
        return WorkTeamUser.objects.filter(groups__name='Company')
    
admin.site.register(WorkTeamUser,WorkStudyUserAdmin)

class StudentAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(StudentWorker)
    
    def changelist_view(self, request, extra_context=None):
        """override to hide inactive students by default"""
        try:
            test = request.META['HTTP_REFERER'].split(request.META['PATH_INFO'])
            if test and test[-1] and not test[-1].startswith('?') and not request.GET.has_key('is_active__exact') and not request.GET.has_key('id__in'):
                return HttpResponseRedirect("/admin/work_study/studentworker/?is_active__exact=1")
        except: pass # In case there is no referer
        return super(StudentAdmin,self).changelist_view(request, extra_context=extra_context)

    def get_fieldsets(self, request, obj=None):
        "Hook for specifying fieldsets for the add form."
        if self.declared_fieldsets:
            fieldsets = self.declared_fieldsets
        else:
            form = self.get_form(request, obj)
            fieldsets = [(None, {'fields': form.base_fields.keys()})]
        for fs in fieldsets:
            fs[1]['fields'] = [f for f in fs[1]['fields'] if self.can_view_field(request, obj, f)]
        return fieldsets
    
    def get_form(self, request, obj=None):
        superclass = super(StudentAdmin, self)
        formclass = superclass.get_form(request, obj)
        for name, field in formclass.base_fields.items():
            if not request.user.is_superuser and name == "ssn":
                self.exclude = ('ssn',)
        return formclass
    
    def can_view_field(self, request, object, field_name):
        "Only allow superuser's to view ssn"
        if not request.user.is_superuser and field_name == "ssn":
            return False
        return True
    
    def render_change_form(self, request, context, *args, **kwargs):
        try:
            if 'original' in context:
                compContacts = Contact.objects.filter(workteam=context['original'].placement)
                context['adminform'].form.fields['primary_contact'].queryset = compContacts
                txt = "<span style=\"color:#444;\"><a href=\"/admin/work_study/timesheet/?q=%s+%s\" target=\"_blank\">Time Sheets for this student</a>" % \
                    (context['original'].fname, context['original'].lname)
                txt += "<br/><a href=\"/admin/work_study/survey/?q=%s+%s\" target=\"_blank\">Surveys for this student</a>" % \
                    (context['original'].fname, context['original'].lname)
                txt += "<br/>Go to work team " + str(context['original'].company())
                if context['original'].placement:
                    txt += "<br/>Company Contacts:"
                    for compContact in compContacts:
                        txt += "<br/>%s %s" % (smart_unicode(compContact.edit_link),compContact.phone)
                txt += '</span>'
                context['adminform'].form.fields['placement'].help_text += txt
        
                # add contact info for pri contact
                if context['original'].primary_contact:
                    txt = '<br/><span style="color:#444;">Number: %s</span>' % (context['original'].primary_contact.phone,)
                    context['adminform'].form.fields['primary_contact'].help_text += txt
        except:
            logging.warning("I coudln't create the student worker added info", exc_info=True, extra={
                'request': request,
            })
        return super(StudentAdmin, self).render_change_form(request, context, *args, **kwargs)
        
    fieldsets = [
        (None, {'fields': ['is_active', ('first_name', 'last_name'), 'mname', 'sex', 'bday', 'day', 'transport_exception',
                           'pic', 'unique_id', 'adp_number', 'ssn', 'username', 'work_permit_no',
                           'year', 'placement', ('school_pay_rate', 'student_pay_rate'),
                           ('am_route','pm_route'), 'primary_contact']}),
        ('Parent and address', {'fields': ['parent_guardian', 'emergency_contacts', 'street',
                                           'city', 'state', 'zip', 'parent_email', 'alt_email'],
            'classes': ['collapse']}),
        ('Personality', {'fields': ['personality_type',], 'classes': ['collapse']}),
    ]
    
    def get_readonly_fields(self, request, obj=None):
        edit_all = Configuration.get_or_default("Edit all Student Worker Fields", "False")
        if edit_all.value == "True":
            return ['parent_guardian', 'street', 'city', 'state', 'zip', 'parent_email', 'alt_email']
        return super(StudentAdmin, self).get_readonly_fields(request, obj=obj)

    inlines = [StudentNumberInline, StudentFileInline, CompanyHistoryInline]
    list_filter = ['day', 'year', 'is_active','placement__cras']
    list_display = ('first_name', 'last_name', 'day', 'company', 'pickUp', 'cra', 'contact')
    search_fields = ['first_name', 'last_name', 'unique_id', 'placement__team_name', 'username', 'id']
    readonly_fields = ['is_active', 'first_name', 'last_name', 'mname', 'sex', 'bday', 'username', 'year', 'parent_guardian', 'street', 'city', 'state', 'zip', 'parent_email', 'alt_email']    
admin.site.register(StudentWorker, StudentAdmin)
admin.site.register(StudentWorkerRoute)
admin.site.register(PresetComment)

class StudentInteractionAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(StudentInteraction)
    
    list_display = ('students', 'date', 'type', 'cra', 'comment_Brief', 'reported_by')
    list_filter = ['type', 'date', 'student','student__is_active']
    search_fields = ['comments', 'student__first_name', 'student__last_name', 'type', 'companies__team_name', 'reported_by__first_name' , 'reported_by__last_name']
    filter_horizontal = ('preset_comment',)
    readonly_fields = ['companies', ]
    fields = ['type', 'student', 'comments', 'preset_comment','companies', 'reported_by']
    
    def lookup_allowed(self, lookup, *args, **kwargs):
        if lookup in ('student__student_ptr__exact', 'student__id__exact',):
            return True
        return super(StudentInteractionAdmin, self).lookup_allowed(lookup, *args, **kwargs)
    
    def save_model(self, request, obj, form, change):
        obj.save()
        try:
            comp = WorkTeam.objects.get(id=obj.student.placement.id)
            cra = CraContact.objects.get(id=comp.cra.id)
            
            msg = str(obj.student) + " had a " + str(obj.get_type_display()) + " meeting on " + str(obj.date) + "\n" + str(obj.comments) + "\n" 
            for comment in obj.preset_comment.all():
                msg += str(comment) + "\n"
            
            send_mail(str(obj.get_type_display()) + " report: " + str(obj.student), msg, str(request.user.email), [cra.email])
        except:
            print >> sys.stderr, "could not send CRA email"
        
admin.site.register(StudentInteraction, StudentInteractionAdmin)

class ContactAdmin(admin.ModelAdmin):
    def render_change_form(self, request, context, *args, **kwargs):
        try:
            comps = WorkTeam.objects.filter(contacts=context['original'].id)
            txt = "Companies linked with"
            for comp in comps:
                txt += "<br/>" + str(comp.edit_link())
            context['adminform'].form.fields['lname'].help_text = txt
        except:
            print >> sys.stderr, "contact admin error, probably from making new one"
        return super(ContactAdmin, self).render_change_form(request, context, args, kwargs)
            
    search_fields = ['fname', 'lname']
    list_display = ('fname','lname',)
    exclude = ('guid',)
admin.site.register(Contact, ContactAdmin)

class TimeSheetPerformanceChoiceAdmin(admin.ModelAdmin):
    list_display = ('edit', 'name', 'rank')
    list_editable = ('name', 'rank')
    
admin.site.register(TimeSheetPerformanceChoice, TimeSheetPerformanceChoiceAdmin)

class TimeSheetAdmin(admin.ModelAdmin):
    def render_change_form(self, request, context, *args, **kwargs):
        if 'original' in context:
            txt = context['original'].student.primary_contact
            context['adminform'].form.fields['supervisor_comment'].help_text = txt
            
            from django.conf import settings
            from django.core.urlresolvers import reverse
            from ecwsp.work_study.views import approve
            url = settings.BASE_URL + reverse(approve) + '?key=' + context['original'].supervisor_key
            context['adminform'].form.fields['approved'].help_text = 'Supervisor Approve Link <a href="%s">%s</a>' % (url,url)
        return super(TimeSheetAdmin, self).render_change_form(request, context, args, kwargs)
        
    search_fields = ['student__first_name', 'student__last_name', 'company__team_name']
    list_filter = [('date', DateRangeFilter),'creation_date', 'approved', 'performance', 'for_pay', 'make_up', 'company',
                   'student__is_active']
    list_display = ('student', 'date', 'company', 'performance', 'student_Accomplishment_Brief', 'supervisor_Comment_Brief',
                    'approved', 'for_pay', 'make_up',)
    readonly_fields = ['hours', 'school_net', 'student_net', 'creation_date']
    exclude = ['supervisor_key']
    actions = [approve]
    date_hierarchy = 'date'
admin.site.register(TimeSheet, TimeSheetAdmin)

admin.site.register(CompanyHistory)

class AttendanceAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(Attendance)
    search_fields = ['student__first_name', 'student__last_name', 'absence_date']
    list_editable = ('makeup_date','reason', 'fee', 'billed')
    list_filter = [('absence_date', DateRangeFilter), 'makeup_date', 'reason', 'fee', 'student','tardy']
    list_display = ('absence_date', 'makeup_date', 'reason', 'fee', 'student', 'billed','tardy')
    fieldsets = [
        (None, {'fields': ['student',('absence_date','makeup_date'),('tardy','tardy_time_in'),
                           ('fee','paid'),'billed','reason',('half_day','waive'),'notes']}),
    ]
    def render_change_form(self, request, context, *args, **kwargs):
        if 'original' in context:
            sis_attendance = context['original'].sis_attendance
            if sis_attendance:
                txt = '<span style="color:#444;">School attendance notes: %s %s</span>' % (sis_attendance.status, sis_attendance.notes)
                context['adminform'].form.fields['notes'].help_text = txt
        return super(AttendanceAdmin, self).render_change_form(request, context, args, kwargs)
admin.site.register(Attendance, AttendanceAdmin)
admin.site.register(AttendanceFee)
admin.site.register(AttendanceReason)
admin.site.register(Personality)

class ClientVisitAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(ClientVisit)
    fieldsets = [
        (None, {'fields': ['date', 'company', 'notify_mentors', 'notes',]}),
        ("DOL", {'fields': ['dol', 'follow_up_of', 'cra', 'student_worker', 'supervisor',
                            'attendance_and_punctuality', 'attitude_and_motivation',
                            'productivity_and_time_management', 'ability_to_learn_new_tasks',
                            'professional_appearance', 'interaction_with_coworkers',
                            'initiative_and_self_direction', 'accuracy_and_attention_to_detail',
                            'organizational_skills', 'observations', 'supervisor_comments',
                            'student_comments', 'job_description', 'work_environment'],
            'classes': ['collapse']}),
    ]
    search_fields = ['company__team_name', 'notes']
    list_display = ('company', 'date', 'comment_brief', 'student_worker')
    list_filter = ['date', 'company', 'cra']
admin.site.register(ClientVisit, ClientVisitAdmin)

class SurveyAdmin(admin.ModelAdmin):
    search_fields = ['student__first_name', 'student__last_name','survey','question','answer','company__team_name']
    list_display = ('survey', 'student', 'question', 'answer', 'date', 'company')
    list_filter = ['survey','question']
admin.site.register(Survey, SurveyAdmin)
admin.site.register(PaymentOption)
admin.site.register(StudentDesiredSkill)
admin.site.register(StudentFunctionalResponsibility)

class CompContractAdmin(admin.ModelAdmin):
    list_display = ('company', 'name', 'signed', 'date', 'number_students', 'school_year')
    list_filter = ('signed','date','school_year')
    search_fields = ('company__name', 'name')
admin.site.register(CompContract, CompContractAdmin)
admin.site.register(MessageToSupervisor)
