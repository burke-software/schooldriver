from api.tests.api_test_base import APITest
from ecwsp.admissions.models import Applicant

class ApplicantTemplateAPIPermissionsTest(APITest):

    def test_template_get_request_as_non_user(self):
        response = self.client.get('/api/application-template/')
        self.assertEqual(response.status_code, 200)

    def test_template_post_request_as_non_user(self):
        data = {"name":"Hello", "json_template":"{}"}
        response = self.client.post('/api/application-template/', data=data)
        self.assertEqual(response.status_code, 403)

    def test_template_get_request_as_non_admin_user(self):
        self.student_login()
        response = self.client.get('/api/application-template/')
        self.assertEqual(response.status_code, 200)

    def test_template_post_request_as_non_admin_user(self):
        self.student_login()
        data = {"name":"Hello", "json_template":"{}"}
        response = self.client.post('/api/application-template/', data=data)
        self.assertEqual(response.status_code, 403)

    def test_template_get_request_as_admin_user(self):
        self.teacher_login()
        response = self.client.get('/api/application-template/')
        self.assertEqual(response.status_code, 200)

    def test_template_post_request_as_admin_user(self):
        self.teacher_login()
        data = {"name":"Hello", "json_template":"{}"}
        response = self.client.post('/api/application-template/', data=data)
        self.assertEqual(response.status_code, 201)




