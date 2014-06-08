from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.db.utils import OperationalError
from ecwsp.sis.sample_data import *
from ecwsp.sis.models import Student

class Command(BaseCommand):
    help = 'Populate blank database'

    def handle(self, *args, **options):
        try:
            if Student.objects.first():
                raise CommandError('You cannot run this on a already populated database')
        except OperationalError: # New database
                call_command('syncdb', all=True, interactive=False)
        SisData().create_all()
        self.stdout.write('Success. Good Job!')
