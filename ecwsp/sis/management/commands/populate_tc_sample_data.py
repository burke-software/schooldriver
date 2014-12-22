from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.db.utils import OperationalError
from ecwsp.sis.sample_tc_data import SampleTCData
from ecwsp.sis.models import Student
from ecwsp.grades.tasks import build_grade_cache

class Command(BaseCommand):
    help = 'Populate blank database with data for TC testing'

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
        self.data = SampleTCData()
        self.data.create_sample_tc_data()
        build_grade_cache()
        self.stdout.write('Success. Good Job!')