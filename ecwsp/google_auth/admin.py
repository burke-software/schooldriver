from django.contrib import admin
from models import *

class GoogleGroupsMappingAdmin(admin.ModelAdmin):
    list_display = ['google_group', 'make_staff','make_superuser']

admin.site.register(GoogleGroupsMapping,GoogleGroupsMappingAdmin)