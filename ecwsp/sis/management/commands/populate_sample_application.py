from django.core.management.base import CommandError, BaseCommand
import os
import json
from ecwsp.admissions.models import ApplicantCustomField, StudentApplicationTemplate

class Command(BaseCommand):
    """ a command line wrapper around the application generator below. Usage:
    $ python manage.py populate_sample_application
    """
    help = 'Populate sample application'

    def handle(self, *args, **options):
        application_generator = ApplicationTemplateGenerator()
        application_generator.create_default_admission_application()
        self.stdout.write('Success. Good Job!')


class ApplicationTemplateGenerator():
    """ a helpful utility to generate a default application for admissions."""

    def create_default_admission_application(self):
        if ApplicantCustomField.objects.first():
            raise CommandError('''You have already generated the default 
            application template; this command only works with a fresh db''')
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

        application_template = self.load_default_application_template()
        self.save_template_as_default_application(application_template)
    
    def load_default_custom_fields(self):
        """ retrieve the hard-coded custom fields from files """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        application_dir = current_dir +  "/../../../admissions/application/"
        file_path = application_dir + "default_custom_fields.json"
        with open(file_path) as data_file:    
            data = json.load(data_file)
        return data

    def load_default_application_template(self):
        """ retrieve the hard-coded applcation template from files """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        application_dir = current_dir +  "/../../../admissions/application/"
        file_path = application_dir + "default_application_template.json"
        with open(file_path) as data_file:    
            data = json.load(data_file)
        return data

    def save_template_as_default_application(self, application_template):
        new_application = StudentApplicationTemplate(
                name = application_template['name'],
                is_default = application_template['is_default'],
                json_template = application_template['json_template']
            )
        new_application.save()


