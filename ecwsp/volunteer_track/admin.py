from volunteer_track.models import *
from django.contrib import admin
from ajax_select import make_ajax_form
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType

from datetime import datetime, date

def approve_site(modeladmin, request, queryset):
    queryset.update(site_approval = 'Accepted')
    for object in queryset:
        LogEntry.objects.log_action(
                    user_id         = request.user.pk, 
                    content_type_id = ContentType.objects.get_for_model(object).pk,
                    object_id       = object.pk,
                    object_repr     = unicode(object), 
                    action_flag     = CHANGE
                )
    
def reject_site(modeladmin, request, queryset):
    queryset.update(site_approval = 'Rejected')
    for object in queryset:
        LogEntry.objects.log_action(
                    user_id         = request.user.pk, 
                    content_type_id = ContentType.objects.get_for_model(object).pk,
                    object_id       = object.pk,
                    object_repr     = unicode(object), 
                    action_flag     = CHANGE
                )
    
def time_fulfilled(modeladmin, request, queryset):
    queryset.update(hours_record=True)
    for object in queryset:
        hrsInstance = Hours(student=object.student, date =  date.today)
        if object.hours_completed():
            if object.hours_completed() < object.hours_required:
                hrsInstance.hours = (object.hours_required) - (object.hours_completed())
                
        else:
            hrsInstance.hours = object.hours_required
        hrsInstance.save()
    LogEntry.objects.log_action(
                    user_id         = request.user.pk, 
                    content_type_id = ContentType.objects.get_for_model(object).pk,
                    object_id       = object.pk,
                    object_repr     = unicode(object), 
                    action_flag     = CHANGE
                )        

class VolunteerAdmin(admin.ModelAdmin):
    form = make_ajax_form(Volunteer, dict(student='student'))
    list_display = ('student', 'site', 'site_supervisor', 'site_approval', 'contract', 'hours_required', 'hours_completed', 'hours_record')
    list_filter = ['site', 'student', 'site_approval', 'contract', 'hours_record']
    search_fields = ['comment', 'student__fname', 'student__lname', 'site__site_name', 'site_supervisor__name']
    actions = [approve_site, reject_site, time_fulfilled]
    
admin.site.register(Volunteer,VolunteerAdmin)
    
class HoursAdmin(admin.ModelAdmin):
    form = make_ajax_form(Hours, dict(student='volunteer'))
    list_display = ('student', 'date', 'hours')
    search_fields = ['student__student__fname', 'student__student__lname']
admin.site.register(Hours,HoursAdmin)
    
class SiteAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'site_address')
    search_fields = ['site_name', 'site_address', 'site_city', 'site_zip', 'site_state']
    
admin.site.register(Site, SiteAdmin)

class SiteSupervisorAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email')
    search_fields = ['name', 'phone', 'email', 'site__site_name', 'site__site_address', 'site__site_city', 'site__site_zip', 'site__site_state']
admin.site.register(SiteSupervisor,SiteSupervisorAdmin)





