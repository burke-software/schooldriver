from django.test import TestCase
from ecwsp.admissions.models import StudentApplicationTemplate

class TestStudentApplicationTemplateModel(TestCase):
    """
    test the implementation of our StudentApplicationTemplate
    """
    def create_simple_application_template(self):
        """
        create a simple application for use with the following tests
        """
        simple_template = {
            'sections' : [
                {'name': 'Personal Information'},
                {'name': 'Contact Information'}
            ]
        }
        new_application = StudentApplicationTemplate()
        new_application.name = 'Simple1'
        new_application.json_template = simple_template
        new_application.save()

    def test_creation_of_simple_template(self):
        self.create_simple_application_template()
        application = StudentApplicationTemplate.objects.get(name='Simple1')
        json_template = application.json_template
        sections = json_template['sections']
        self.assertEqual(len(sections), 2)
        self.assertEqual(sections[0]['name'], 'Personal Information')
        
