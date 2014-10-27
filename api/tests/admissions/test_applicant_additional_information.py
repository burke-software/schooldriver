from api.tests.api_test_base import APITest
from ecwsp.admissions.models import ApplicantAdditionalInformation, Applicant

class ApplicantAdditionalInformationAPIGetTest(APITest):

    def test_single_create_additional_information(self):
        self.teacher_login()
        applicant = {
            "fname" : "Timmy",
            "lname" : "Student",
            "sex" : "M"
        }
        previous_count = ApplicantAdditionalInformation.objects.count()
        response = self.client.post('/api/applicant/', data = applicant)
        applicant_id = response.data["id"]
        data = {
            "applicant": applicant_id,
            "question" : "hello", 
            "answer" : "world"
        }
        
        response = self.client.post('/api/applicant-additional-information/', data)
        new_count = ApplicantAdditionalInformation.objects.count()
        self.assertEqual(new_count, previous_count + 1)

    def test_bulm_create_additional_information(self):
        self.teacher_login()
        applicant = {
            "fname" : "Timmy",
            "lname" : "Student",
            "sex" : "M"
        }
        previous_count = ApplicantAdditionalInformation.objects.count()
        response = self.client.post('/api/applicant/', data = applicant)
        applicant_id = response.data["id"]
        data = [
            {"applicant": applicant_id, "question" : "hello", "answer" : "world"},
            {"applicant": applicant_id, "question" : "hello-again", "answer" : "still world"}
        ]
        response = self.client.post('/api/applicant-additional-information/', data)
        print(response)
        new_count = ApplicantAdditionalInformation.objects.count()
        self.assertEqual(new_count, previous_count + 2)
        
    





