from api.tests.api_test_base import APITestBase
from ecwsp.grades.models import Grade
import json

class GradeAPITest(APITestBase):
    """
    test the implementation of our grades api
    """

    def test_admin_user_access(self):
        """
        only an admin user should be able to access the grade api
        """
        # try with a non-authenticated user
        response = self.client.get('/api/grades/')
        self.assertEqual(response.status_code, 403)

        # try with a non-admin user
        self.login_normal_user()
        response = self.client.get('/api/grades/')
        self.assertEqual(response.status_code, 403)

        # now try with a legit admin user!
        self.login_admin_user()
        response = self.client.get('/api/grades/')
        self.assertEqual(response.status_code, 200)

    def test_post_request(self):
        """
        test a post request for a student's grade using the api
        """
        # login as admin user
        self.login_admin_user()

        # make sure no grades currently exist!
        response = self.client.get('/api/grades/')
        number_of_grades = len(json.loads(response.content))
        self.assertEqual(number_of_grades, 0)

        # add a new grade
        course = self.create_test_course()
        marking_period = self.create_test_marking_period()
        student = self.create_test_student()
        data = {
            'student_id': student.id,
            'course' : course.id,
            'marking_period' : marking_period.id,
            'grade' : 95,
            'override_final' : False,
            'comment' : 'a job well done',
        }

        # test the post response
        response = self.client.post('/api/grades/', data)
        json_response = json.loads(response.content)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(json_response['comment'], 'a job well done')

        # make sure a new grade was added!
        response = self.client.get('/api/grades/')
        number_of_grades = len(json.loads(response.content))
        self.assertEqual(number_of_grades, 1)

    def test_put_request(self):
        """
        use the api to modify an existing grade
        """
        # let's first post a grade
        self.login_admin_user()
        course = self.create_test_course()
        marking_period = self.create_test_marking_period()
        student = self.create_test_student()
        data = {
            'student_id': student.id,
            'course' : course.id,
            'marking_period' : marking_period.id,
            'grade' : 70,
            'override_final' : False,
            'comment' : 'a decent job, needs some work',
        }
        response = self.client.post('/api/grades/', data)
        grade_data = json.loads(response.content)

        # change the grade and a comment
        grade_data['grade'] = 100
        grade_data['comment'] = "much better dude!"

        # put the change
        response = self.client.put(
            '/api/grades/%s/' % grade_data['id'],
             json.dumps(grade_data),
             content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        new_grade = json.loads(response.content)

        # check if it updated in the response!
        self.assertEqual(new_grade['grade'], '100')





