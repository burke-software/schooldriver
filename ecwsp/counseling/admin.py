from django.contrib import admin
from django.forms import CheckboxSelectMultiple

from ajax_select import make_ajax_form
from models import *

class StudentMeetingAdmin(admin.ModelAdmin):
   list_display = ['display_students','date','reported_by']
   fields = ['students','date','notes','follow_up_action','follow_up_notes','reported_by']
   form = make_ajax_form(StudentMeeting, dict(students='student'))
   def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'reported_by':
            kwargs['initial'] = request.user.id
            return db_field.formfield(**kwargs)
        return super(StudentMeetingAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs
        )

admin.site.register(StudentMeeting, StudentMeetingAdmin)
admin.site.register(FollowUpAction)

admin.site.register(ReferralCategory)
admin.site.register(ReferralReason)

class ReferralFormAdmin(admin.ModelAdmin):
    list_display = ['classroom_teacher','date','referred_by','student']
    list_filer = ['classroom_teacher','date','referred_by','student']
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }
    form = make_ajax_form(ReferralForm, dict(student='student'))
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ['referred_by','classroom_teacher']:
            kwargs['initial'] = request.user.id
            return db_field.formfield(**kwargs)
        return super(ReferralFormAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs
        )
admin.site.register(ReferralForm,ReferralFormAdmin)

