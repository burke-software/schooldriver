from django.test import Client, TestCase
from ecwsp.admissions.views import student_application
from django.core.urlresolvers import reverse

class TestGetRequests(TestCase):

    def setUp(self):
        self.client = Client()

    def test_simple_get_request_for_200_code(self):
        response = self.client.get(reverse('student-application'))
        self.assertEquals(response.status_code, 200)




