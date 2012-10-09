from django.shortcuts import get_object_or_404
from django.contrib import admin
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from ajax_select import make_ajax_form
from ajax_select.fields import autoselect_fields_check_can_add

from custom_field.custom_field import CustomFieldAdmin
from ecwsp.admissions.models import AdmissionCheck, ContactLog, EthnicityChoice, ReligionChoice, FeederSchool
from ecwsp.admissions.models import SchoolType, OpenHouse, HeardAboutUsOption, FirstContactOption
from ecwsp.admissions.models import PlaceOfWorship, ApplicationDecisionOption, WithdrawnChoices
from ecwsp.admissions.models import BoroughOption, CountryOption, ImmigrationOption, AdmissionLevel
from ecwsp.admissions.models import Applicant
from ecwsp.admissions.forms import ApplicantForm

import re

admin.site.register(EthnicityChoice)
admin.site.register(ReligionChoice)
admin.site.register(FeederSchool)
admin.site.register(SchoolType)
admin.site.register(OpenHouse)
admin.site.register(ContactLog)
admin.site.register(HeardAboutUsOption)
admin.site.register(FirstContactOption)
admin.site.register(PlaceOfWorship)
admin.site.register(ApplicationDecisionOption)
admin.site.register(WithdrawnChoices)
admin.site.register(BoroughOption)
admin.site.register(CountryOption)
admin.site.register(ImmigrationOption)

class AdmissionCheckInline(admin.TabularInline):
    model = AdmissionCheck
    extra = 0
    verbose_name_plural = "Items needed to be completed to attain this level in the process"

class AdmissionLevelAdmin(admin.ModelAdmin):
    list_display = ('edit','name', 'order','show_checks')
    list_display_links = ('edit',)
    list_editable = ('name','order',)
    inlines = (AdmissionCheckInline,)
admin.site.register(AdmissionLevel,AdmissionLevelAdmin)

class ContactLogInline(admin.TabularInline):
    model = ContactLog
    extra = 1
    readonly_fields = ('user',)

class ApplicantAdmin(CustomFieldAdmin):
    form = ApplicantForm
    list_display = ('lname', 'fname', 'present_school', 'city', 'level', 'application_decision',
                    'school_year', 'ready_for_export','follow_up_date')
    list_filter = ['school_year', 'level', 'checklist', 'ready_for_export',
                   'application_decision','present_school','ethnicity', 'heard_about_us', 'first_contact', 'year']
    search_fields = ['lname', 'fname', 'present_school__name']
    inlines = [ContactLogInline]
    ordering = ('-id',)
    fieldsets = [
        (
            None,
            {'fields': [
                'ready_for_export', 'lname', 'fname', 'mname', 'pic', 'bday', 'present_school', 'heard_about_us', 'first_contact',
                'application_decision', 'application_decision_by', 'withdrawn_note', 'total_income', 'adjusted_available_income',
                'calculated_payment']
            }
        ),
        (
            'About applicant',
            {'fields': [
                ('ssn', 'sex'), ('ethnicity',), 'follow_up_date', ('religion','place_of_worship'), ('year', 'school_year'),
                ('hs_grad_yr','elem_grad_yr'), 'email', 'notes', 'siblings', 'borough', ('country_of_birth','immigration_status'),
                'family_preferred_language', ('lives_with', 'first_to_college'), 'individual_education_plan', 'parent_guardians', 'open_house_attended'],
            'classes': ['collapse']}
        ),
    ]
    
    def get_form(self, request, obj=None, **kwargs):
        form = super(ApplicantAdmin,self).get_form(request,obj,**kwargs)
        autoselect_fields_check_can_add(form,self.model,request.user)
        return form
    
    def add_view(self, request, form_url='', extra_context=None):
        levels = []
        for level in AdmissionLevel.objects.all():
            level.checks = []
            level.max = 0
            for check in AdmissionCheck.objects.filter(level=level):
                level.checks.append(check)
                level.max += 1
            levels.append(level)
        my_context = {
            'levels': levels,
            'current_level': None
        }
        return super(ApplicantAdmin, self).add_view(request, form_url, extra_context=my_context)
    
    def change_view(self, request, object_id, extra_context=None):
        levels = []
        applicant = get_object_or_404(Applicant,id=object_id)
        for level in AdmissionLevel.objects.all():
            level.checks = []
            level.max = 0
            for check in AdmissionCheck.objects.filter(level=level):
                level.checks.append(check)
                level.max += 1
                if object_id:
                    if check in applicant.checklist.all():
                        check.checked = True
                    else:
                        check.checked = False
            levels.append(level)
           
        my_context = {
            'levels': levels,
            'current_level': applicant.level,
        }
        return super(ApplicantAdmin, self).change_view(request, object_id, extra_context=my_context)
    
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, ContactLog) and instance.note: #Check if it is the correct type of inline
                if(not instance.user):
                    instance.user = request.user        
                instance.save()
    
    def save_model(self, request, obj, form, change):
        if 'checkmark_data' in request.POST: # This confirms the checks are there, in case we call this from somewhere odd say mass-edit.
            if not obj.id:
                obj.save()
            input_checks = []
            for data in request.POST:
                if re.match("check_", data):
                    id = data.split('_')[3]
                    check = AdmissionCheck.objects.get(id=id)
                    input_checks.append(check)
            for check in obj.checklist.all():
                if not check in input_checks:
                    obj.checklist.remove(check)
                    contact_log = ContactLog(
                        user = request.user,
                        applicant = obj,
                        note = "%s removed" % (check,)
                    )
                    contact_log = ContactLog(
                        user = request.user,
                        applicant = obj,
                        note = "%s removed" % (check,)
                    )
                    contact_log.save()
                    LogEntry.objects.log_action(
                        user_id         = request.user.pk, 
                        content_type_id = ContentType.objects.get_for_model(obj).pk,
                        object_id       = obj.pk,
                        object_repr     = unicode(obj), 
                        action_flag     = CHANGE,
                        change_message  = "Unchecked " + unicode(check)
                    )
            for check in input_checks:
                if not check in obj.checklist.all():
                    obj.checklist.add(check)
                    contact_log = ContactLog(
                        user = request.user,
                        applicant = obj,
                        note = "%s completed" % (check,)
                    )
                    contact_log.save()
                    LogEntry.objects.log_action(
                        user_id         = request.user.pk, 
                        content_type_id = ContentType.objects.get_for_model(obj).pk,
                        object_id       = obj.pk,
                        object_repr     = unicode(obj), 
                        action_flag     = CHANGE,
                        change_message  = "Checked " + unicode(check)
                    )
        super(ApplicantAdmin, self).save_model(request, obj, form, change)
        if obj.application_decision and obj.application_decision.level.all().count() \
        and obj.application_decision and not obj.level in obj.application_decision.level.all():
            msg = 'WARNING: Decision %s should be on level(s) ' % (obj.application_decision,)
            for level in obj.application_decision.level.all():
                msg += '%s, ' % (level,)
            messages.warning(request, msg[:-2])
    
admin.site.register(Applicant, ApplicantAdmin)
