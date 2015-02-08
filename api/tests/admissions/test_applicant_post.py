from api.tests.api_test_base import APITest
from ecwsp.admissions.models import Applicant, ApplicantAdditionalInformation, ReligionChoice

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

    def test_post_request_containing_related_field(self):
        self.teacher_login()
        valid_religion_choice = ReligionChoice.objects.all().first()
        data = {
            "fname" : "Timmy",
            "lname" : "Student",
            "sex" : "M",
            "religion" : valid_religion_choice.id,
        }
        previous_applicant_count = Applicant.objects.count()
        response = self.client.post('/api/applicant/', data = data)
        self.assertEqual(response.status_code, 201)
        post_appilcant_count = Applicant.objects.count()
        self.assertEqual(previous_applicant_count + 1, post_appilcant_count)



