from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.db.utils import OperationalError
from ecwsp.sis.sample_data import *
from ecwsp.sis.models import Student
from ecwsp.grades.tasks import *

class Command(BaseCommand):
    help = 'Populate blank database with data for Balt testing'

    def handle(self, *args, **options):
        try:
            if Student.objects.first():
                raise CommandError('You cannot run this on a already populated database')
        except OperationalError: # New database
            import django
            if django.get_version()[:3] != '1.7':
                call_command('syncdb', all=True, interactive=False)
            else:
                call_command('migrate', interactive=False)
        self.data = SisData()
        self.stdout.write('Creating grade scale data...')
        self.data.create_grade_scale_data()
        self.stdout.write('Creating data for a sample honors student...')
        self.data.create_sample_honors_and_ap_data()
        self.stdout.write('Building grade cache...')
        build_grade_cache()
        self.stdout.write('Success. Good Job!')
