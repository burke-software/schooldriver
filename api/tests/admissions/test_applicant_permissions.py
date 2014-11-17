from api.tests.api_test_base import APITest
from ecwsp.admissions.models import Applicant

class ApplicantAPIPermissionsTest(APITest):

    def test_applicant_get_request_as_non_user(self):
        response = self.client.get('/api/applicant/')
        self.assertEqual(response.status_code, 403)

    def test_applicant_options_request_as_non_user(self):
        response = self.client.options('/api/applicant/')
        self.assertEqual(response.status_code, 200)

    def test_applicant_post_request_as_non_user(self):
        data = {"fname":"Hello", "lname":"World"}
        response = self.client.post('/api/applicant/', data=data)
        self.assertEqual(response.status_code, 201)

    def test_applicant_get_request_as_non_admin_user(self):
        self.student_login()
        response = self.client.get('/api/applicant/')
        self.assertEqual(response.status_code, 403)

    def test_applicant_options_request_as_non_admin_user(self):
        self.student_login()
        response = self.client.options('/api/applicant/')
        self.assertEqual(response.status_code, 200)

    def test_applicant_post_request_as_non_admin_user(self):
        self.student_login()
        data = {"fname":"Hello", "lname":"World"}
        response = self.client.post('/api/applicant/', data=data)
        self.assertEqual(response.status_code, 201)

    def test_applicant_get_request_as_admin_user(self):
        self.teacher_login()
        response = self.client.get('/api/applicant/')
        self.assertEqual(response.status_code, 200)

    def test_applicant_options_request_as_admin_user(self):
        self.teacher_login()
        response = self.client.options('/api/applicant/')
        self.assertEqual(response.status_code, 200)

    def test_applicant_post_request_as_admin_user(self):
        self.teacher_login()
        data = {"fname":"Hello", "lname":"World"}
        response = self.client.post('/api/applicant/', data=data)
        self.assertEqual(response.status_code, 201)




