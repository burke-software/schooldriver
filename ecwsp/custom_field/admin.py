from django.contrib import admin

from ecwsp.custom_field.models import *

class CustomFieldAdmin(admin.ModelAdmin):
    list_display = ('content_type','name')
    list_filter = ('content_type',)
    search_fields = ('content_type__name','name')
admin.site.register(CustomField, CustomFieldAdmin)