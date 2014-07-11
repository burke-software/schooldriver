from api.tests.api_test_base import APITest

class GradeAPIGetTest(APITest):
    """
    test that various Grade API get requests are working as expected
    """

    def test_get_all_grades(self):
        """
        an admin user should be able to retreive all grades in the system
        """
        self.teacher_login()
        response = self.client.get('/api/grades/')
        # there are currently only 5 grades in the sample_data
        self.assertEqual(len(response.data), 5)

    def test_get_specific_grade(self):
        """
        test a get request for a grade with a specific id
        """
        self.teacher_login()
        response = self.client.get('/api/grades/1/')
        self.assertEqual(response.data['grade'], 50)

        # test another grade instance just to be certain
        response = self.client.get('/api/grades/2/')
        self.assertEqual(float(response.data['grade']), float(89.09))

    def test_student_filter(self):
        """
        test a get request using the filter parameter "student"
        """
        self.teacher_login()
        # attempting to get a response from '/api/grades/?student=1'
        response = self.client.get('/api/grades/', {'student': 1})
        # there should be 2 grade instances for this student
        self.assertEqual(len(response.data), 2)

        #let's try another student
        response = self.client.get('/api/grades/', {'student': 3})
        self.assertEqual(len(response.data), 1)

    def test_multiple_filters(self):
        """
        test a get request with multiple filters specified
        """
        self.teacher_login()
        filters = {'student': 2, 'course_section': 1}
        response = self.client.get('/api/grades/', filters)
        self.assertEqual(len(response.data), 1)

    def test_ungraded_courses(self):
        """
        grades should not appear from courses that are "ungraded"
        """
        self.teacher_login()
        # change the first course to be non-graded
        self.data.course.graded = False
        self.data.course.save()

        # none of the grades from that course should be retured by the API
        # since all of the grades were from this course, the length is '0'
        response = self.client.get('/api/grades/')
        self.assertEqual(len(response.data), 0)

        # Now let's set it back and hopefully things work as expected again
        self.data.course.graded = True
        self.data.course.save()
        response = self.client.get('/api/grades/')
        self.assertEqual(len(response.data), 5)











