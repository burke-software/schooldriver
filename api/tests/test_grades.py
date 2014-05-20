from api.tests.api_test_base import APITest
from ecwsp.grades.models import Grade
import json

class GradeAPITest(APITest):
    """
    test the implementation of our grades api
    """

    def test_simple_get_request(self):
        """
        test a simple get request with both auth'd and non-auth'd users
        """

        # try it with a no authentication
        response = self.client.get('/api/grades/')
        self.assertEqual(response.status_code, 403)

        # try it with a normal user (authenticated but wrong permissions)
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/grades/')
        self.assertEqual(response.status_code, 403)

        # sign out...
        self.client.force_authenticate(user=None)

        # try it with an admin user (authenticated)
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/grades/')
        self.assertEqual(response.status_code, 200)

    def test_simple_post_request(self):
        """
        test a post request for a student's grade using the api
        """
        # make sure no grades currently exist!
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/grades/')
        number_of_grades = len(json.loads(response.content))
        self.assertEqual(number_of_grades, 0)

        # create a new grade
        enrollment = self.enroll_student_in_test_section()
        data = {
            'student_id': enrollment.user.id,
            'course' : enrollment.section.id,
            'marking_period' : enrollment.section.marking_period.id,
            'grade' : 95,
            'override_final' : False,
            'comment' : 'a job well done',
        }
        response = self.client.post('/api/grades/', data)
        self.assertEqual(response.status_code, 200)
