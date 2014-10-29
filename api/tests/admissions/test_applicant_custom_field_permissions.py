from api.tests.api_test_base import APITest
from ecwsp.admissions.models import Applicant

class ApplicantCustomFieldAPIPermissionsTest(APITest):

    def test_custom_field_get_request_as_non_user(self):
        response = self.client.get('/api/applicant-custom-field/')
        self.assertEqual(response.status_code, 200)

    def test_custom_field_post_request_as_non_user(self):
        response = self.client.post('/api/applicant-custom-field/', data={})
        self.assertEqual(response.status_code, 403)

    def test_custom_field_get_request_as_non_admin_user(self):
        self.student_login()
        response = self.client.get('/api/applicant-custom-field/')
        self.assertEqual(response.status_code, 200)

    def test_custom_field_post_request_as_non_admin_user(self):
        self.student_login()
        response = self.client.post('/api/applicant-custom-field/', data={})
        self.assertEqual(response.status_code, 403)

    def test_custom_field_get_request_as_admin_user(self):
        self.teacher_login()
        response = self.client.get('/api/applicant-custom-field/')
        self.assertEqual(response.status_code, 200)

    def test_custom_field_post_request_as_admin_user(self):
        self.teacher_login()
        response = self.client.post('/api/applicant-custom-field/', data={})
        self.assertEqual(response.status_code, 201)




