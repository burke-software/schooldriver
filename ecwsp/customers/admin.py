from django.conf import settings
if settings.MULTI_TENANT:
    from django.contrib import admin
    from .models import Client

    class ClientAdmin(admin.ModelAdmin):
        model = Client
        list_display = ('name', 'schema_name', 'on_trial', 'paid_until',)
        search_fields = ('name', 'schema_name',)
        list_filter = ('on_trial',)
    admin.site.register(Client, ClientAdmin)
