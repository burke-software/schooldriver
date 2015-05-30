from django.contrib import admin
from django.contrib.admin.models import LogEntry
from reversion import VersionAdmin
from .models import Configuration, AccessLog, Template
from .forms import TemplateForm


class ConfigurationAdmin(admin.ModelAdmin):
    search_fields = ['name']

admin.site.register(Configuration, ConfigurationAdmin)


class AccessLogAdmin(admin.ModelAdmin):
    list_display = ('login', 'usage', 'date', 'os', 'browser')
    search_fields = ['login__username', 'login__first_name']
admin.site.register(AccessLog, AccessLogAdmin)


class LogEntryAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'action_time', 'content_type', 'object_repr', 'is_addition',
        'is_deletion', 'is_change')
    list_filter = ('action_flag', 'action_time')
    search_fields = ['user__username', 'content_type__name', 'object_repr']
    readonly_fields = (
        'user', 'action_time', 'content_type', 'object_repr', 'action_flag',
        'object_id', 'change_message', 'action_time')
admin.site.register(LogEntry, LogEntryAdmin)


class TemplateAdmin(VersionAdmin):
    form = TemplateForm
admin.site.register(Template, TemplateAdmin)
