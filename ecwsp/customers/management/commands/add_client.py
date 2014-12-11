from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from ecwsp.customers.models import Client

class Command(BaseCommand):
    args = '<domain_url> <schema_name> <name>'
    help = 'Creates a new client'

    def handle(self, domain_url, schema_name, name, **kwargs):
        if not settings.MULTI_TENANT:
            raise CommandError('MULTI_TENANT must be enabled to add a client')
        Client.objects.create(domain_url=domain_url, schema_name=schema_name, name=name)
