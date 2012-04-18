from ecwsp.sis.models import *
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Run daily tasks such as attendance statistics'
    
    def handle(self, *args, **options):
        stat = AttendanceDailyStat()
        stat.set_all()
