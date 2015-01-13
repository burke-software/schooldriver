from api.tests.api_test_base import APITest
from ecwsp.admissions.models import ApplicantAdditionalInformation
from ecwsp.admissions.models import Applicant
from ecwsp.admissions.models import ApplicantCustomField


class ApplicantAdditionalInformationAPIGetTest(APITest): 
    sample_applicant = {
            "fname" : "Timmy",
            "lname" : "Student",
            "sex" : "M",
        }

    def test_single_create_additional_information(self):
        self.teacher_login()
        applicant = self.sample_applicant
        new_custom_field = ApplicantCustomField()
        new_custom_field.save()
        previous_count = ApplicantAdditionalInformation.objects.count()
        response = self.client.post('/api/applicant/', data = applicant)
        applicant_id = response.data["id"]
        data = {
            "applicant": applicant_id,
            "custom_field" : new_custom_field.id, 
            "answer" : "world"
        }
        
        response = self.client.post('/api/applicant-additional-information/', data)
        new_count = ApplicantAdditionalInformation.objects.count()
        self.assertEqual(new_count, previous_count + 1)

    def test_bulk_create_additional_information(self):
        self.teacher_login()
        applicant = self.sample_applicant
        new_custom_field = ApplicantCustomField()
        new_custom_field.save()
        previous_count = ApplicantAdditionalInformation.objects.count()
        response = self.client.post('/api/applicant/', data = applicant)
        applicant_id = response.data["id"]
        data = [
            {"applicant": applicant_id, "custom_field" : new_custom_field.id, "answer" : "world"},
            {"applicant": applicant_id, "custom_field" : new_custom_field.id, "answer" : "still world"}
        ]
        response = self.client.post('/api/applicant-additional-information/', data)
        new_count = ApplicantAdditionalInformation.objects.count()
        self.assertEqual(new_count, previous_count + 2)
        
    





