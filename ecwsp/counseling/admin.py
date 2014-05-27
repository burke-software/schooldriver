from django.contrib import admin
from django.db import models
from django.forms import CheckboxSelectMultiple

from .models import StudentMeeting, StudentMeetingCategory, FollowUpAction
from .models import ReferralCategory, ReferralReason, ReferralForm
import autocomplete_light

class StudentMeetingAdmin(admin.ModelAdmin):
    list_display = ['category','display_students','date','reported_by']
    fields = ['category','students','date','notes','file','follow_up_action','follow_up_notes','reported_by']
    form = autocomplete_light.modelform_factory(StudentMeeting)
    
    search_fields = ['students__username', 'students__last_name', 'students__first_name', 'category__name', 'reported_by__username']
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'reported_by':
            kwargs['initial'] = request.user.id
            return db_field.formfield(**kwargs)
        return super(StudentMeetingAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
    
    def lookup_allowed(self, lookup, *args, **kwargs):
        if lookup in ('students__id__exact',):
            return True
        return super(StudentMeetingAdmin, self).lookup_allowed(lookup, *args, **kwargs)

admin.site.register(StudentMeeting, StudentMeetingAdmin)
admin.site.register(StudentMeetingCategory)
admin.site.register(FollowUpAction)

admin.site.register(ReferralCategory)
admin.site.register(ReferralReason)

class ReferralFormAdmin(admin.ModelAdmin):
    list_display = ['classroom_teacher','date','referred_by','student']
    list_filer = ['classroom_teacher','date','referred_by','student']
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }
    form = autocomplete_light.modelform_factory(ReferralForm)
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ['referred_by','classroom_teacher']:
            kwargs['initial'] = request.user.id
            return db_field.formfield(**kwargs)
        return super(ReferralFormAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs
        )
admin.site.register(ReferralForm,ReferralFormAdmin)

