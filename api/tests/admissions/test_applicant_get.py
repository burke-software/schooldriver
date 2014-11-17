from api.tests.api_test_base import APITest
from ecwsp.admissions.models import Applicant

class ApplicantAPIGetTest(APITest):

    def test_simple_get_request_for_200_code(self):
        self.teacher_login()
        response = self.client.get('/api/applicant/')
        self.assertEqual(response.status_code, 200)

    





