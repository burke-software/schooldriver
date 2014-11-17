from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.db.utils import OperationalError
from ecwsp.admissions.models import ApplicantCustomField

class Command(BaseCommand):
    help = 'delete all existing custom fields'

    def handle(self, *args, **options):
        if not ApplicantCustomField.objects.first():
            raise CommandError('there are no fields to remove!')
        else:
            for f in ApplicantCustomField.objects.all():
                f.delete()


