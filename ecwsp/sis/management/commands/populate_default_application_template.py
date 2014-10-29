from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.db.utils import OperationalError
import os
import json
import requests
from ecwsp.admissions.models import ApplicantCustomField, StudentApplicationTemplate

class Command(BaseCommand):
    help = 'Populate default application template'

    def load_default_custom_fields(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        application_dir = current_dir +  "/../../../admissions/application/"
        file_path = application_dir + "default_custom_fields.json"
        with open(file_path) as data_file:    
            data = json.load(data_file)
        return data

    def load_default_application_template(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        application_dir = current_dir +  "/../../../admissions/application/"
        file_path = application_dir + "default_application_template.json"
        with open(file_path) as data_file:    
            data = json.load(data_file)
        return data

    def handle(self, *args, **options):
        if ApplicantCustomField.objects.first():
            raise CommandError('You have already generated the default fields')
        else:
            default_custom_fields = self.load_default_custom_fields()
            for field in default_custom_fields:
                f = ApplicantCustomField(
                    field_name = field['field_name'],
                    is_field_integrated_with_applicant = field['is_field_integrated_with_applicant'],
                    field_type = field['field_type'],
                    field_label = field['field_label'],
                    field_choices = field['field_choices'],
                    helptext = field['helptext'],
                    required = field['required']
                )
                f.id = field['id']
                f.save()

