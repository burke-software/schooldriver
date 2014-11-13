from django.test import TestCase
from ecwsp.admissions.models import StudentApplicationTemplate
from ecwsp.admissions.application.default_template import DefaultTemplate

class TestDefaultTemplate(TestCase):

    def test_loading_of_default_template(self):
        new_application = DefaultTemplate()
        new_application.save_model_in_database()
        saved_application = StudentApplicationTemplate.objects.get(is_default = True)
        json_template = saved_application.json_template
        self.assertEqual(json_template['sections'][0]['name'], 'Personal Information')
        self.assertEqual(json_template['sections'][1]['name'], 'Family Information')

    