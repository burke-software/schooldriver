import json
import os
from ecwsp.admissions.models import StudentApplicationTemplate

class DefaultTemplate:
    json_template = ''

    def __init__(self):
        self.load_default_template_from_json_file()

    def load_default_template_from_json_file(self):
        this_directory_path = os.path.dirname(os.path.realpath(__file__))
        json_file_path = this_directory_path + '/raw_default_template.json'
        with open(json_file_path) as default_template:    
            self.json_template = json.load(default_template)

    def save_model_in_database(self):
        newApplicationTemplate = StudentApplicationTemplate()
        newApplicationTemplate.name = 'Default Template'
        newApplicationTemplate.is_default = True
        newApplicationTemplate.json_template = self.json_template
        newApplicationTemplate.save()