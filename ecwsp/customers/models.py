from django.db import models
from django.conf import settings
if settings.MULTI_TENANT:
    from tenant_schemas.models import TenantMixin

    class Client(TenantMixin):
        name = models.CharField(max_length=100)
        paid_until =  models.DateField(blank=True, null=True)
        on_trial = models.BooleanField(default=True)
        created_on = models.DateField(auto_now_add=True)

