from api.tests.api_test_base import APITest
from ecwsp.admissions.models import Applicant

class ApplicantAPIPostTest(APITest):

    def test_simple_post_request(self):
        self.teacher_login()
        data = {
            "fname" : "Timmy",
            "lname" : "Student",
            "sex" : "M"
        }
        previous_applicant_count = Applicant.objects.count()
        response = self.client.post('/api/applicant/', data = data)
        self.assertEqual(response.status_code, 201)
        post_appilcant_count = Applicant.objects.count()
        self.assertEqual(previous_applicant_count + 1, post_appilcant_count)

