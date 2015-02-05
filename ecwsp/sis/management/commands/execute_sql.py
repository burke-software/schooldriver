
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.db.utils import OperationalError
from ecwsp.admissions.models import ApplicantCustomField
from ecwsp.customers.models import Client
from django.db import connection
import os

class Command(BaseCommand):
    help = 'run raw SQL command from a file'

    def handle(self, *args, **options):
        current_schema = connection.schema_name
        sql_string = self.load_sql_command_from_file()
        if current_schema == "public":
            self.stdout.write('Running raw sql command for all schemas...')
        else: 
            client = Client.objects.get( schema_name = current_schema )
            self.stdout.write("Running raw sql command for %s (%s)" % (client.schema_name, client.name))
        with connection.cursor() as c:
            c.execute(sql_string)

    def load_sql_command_from_file(self):
        """ load the sql from the raw_sql_file.sql into a string """
        this_folder = os.path.dirname(os.path.realpath(__file__))
        output_file_path = this_folder + "/raw_sql_file.sql"
        with open (output_file_path, "r") as myfile:
            sql_string = myfile.read().replace('\n', '')
        return sql_string