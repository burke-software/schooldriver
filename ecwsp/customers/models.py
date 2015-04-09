from django.db import models
from tenant_schemas.models import TenantMixin


class Client(TenantMixin):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    paid_until = models.DateField(blank=True, null=True)
    on_trial = models.BooleanField(default=True)
    created_on = models.DateField(auto_now_add=True)


class SignUp(models.Model):
    status_choices = (
        ('S', 'Started'),
        ('D', 'Done'),
        ('F', 'Failed'),
    )
    name = models.CharField(max_length=100, unique=True)
    domain_url = models.CharField(max_length=100, unique=True)
    client_name = models.CharField(max_length=100)
    client_email = models.EmailField()
    client_number = models.CharField(max_length=10, blank=True)
    status = models.CharField(max_length=1, default='S', choices=status_choices)
