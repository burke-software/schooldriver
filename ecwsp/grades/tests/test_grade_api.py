from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from ecwsp.sis.sample_data import SisData
from ecwsp.sis.tests import SisTestMixin


class GradeApiTests(SisTestMixin, APITestCase):
    def setUp(self):
        self.data = SisData()
        self.data.create_basics()
        self.client = APIClient()

    def test_set_grade(self):
        data = {
            "student": self.data.student.id,
            "marking_period": self.data.marking_period.id,
            "course_section": self.data.course_section.id,
            "grade": "21",
        }
        response = self.client.post(reverse('api-set-grade'), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = {
            "student": self.data.student.id,
            "marking_period": self.data.marking_period.id,
            "grade": "21",
        }
        response = self.client.post(reverse('api-set-grade'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = {
            "marking_period": self.data.marking_period.id,
            "enrollment": self.data.course_enrollment.id,
            "grade": "21",
        }
        response = self.client.post(reverse('api-set-grade'), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_set_final_grade(self):
        data = {
            "student": self.data.student.id,
            "course_section": self.data.course_section.id,
            "grade": "21",
        }
        response = self.client.post(reverse('api-set-final-grade'), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = {
            "student": self.data.student.id,
            "grade": "21",
        }
        response = self.client.post(reverse('api-set-final-grade'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = {
            "enrollment": self.data.course_enrollment.id,
            "grade": "21",
        }
        response = self.client.post(reverse('api-set-final-grade'), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
