from api.tests.api_test_base import APITest
from ecwsp.grades.models import Grade
from ecwsp.schedule.models import CourseEnrollment
from decimal import Decimal
import logging

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
        num_grades = Grade.objects.count()
        self.assertEqual(len(response.data), num_grades)

    def test_get_specific_grade(self):
        """
        test a get request for a grade with a specific id
        """
        self.teacher_login()
        known_grade = Grade.objects.all().first()
        response = self.client.get('/api/grades/%s/' % known_grade.id)
        expected_grade = known_grade.grade
        self.assertEqual(Decimal(response.data['grade']), expected_grade)

    def test_student_filter(self):
        """
        test a get request using the filter parameter "student"
        """
        self.teacher_login()
        # attempting to get a response from '/api/grades/?student=1'
        response = self.client.get('/api/grades/', {'student': 1})
        num_grades = Grade.objects.filter(
            student_id=1
            ).count()
        # there should be 2 grade instances for this student
        self.assertEqual(len(response.data), num_grades)

        #let's try another student
        response = self.client.get('/api/grades/', {'student': 3})
        num_grades = Grade.objects.filter(
            student_id=3
            ).count()
        self.assertEqual(len(response.data), num_grades)

    def test_multiple_filters(self):
        """
        test a get request with multiple filters specified
        """
        self.teacher_login()
        known_student = self.data.student2
        known_course_section = self.data.course_section2
        expected_grade_count = Grade.objects.filter(
            student = known_student, 
            course_section = known_course_section
            ).count()

        filters = {
            'student': known_student.id, 
            'course_section': known_course_section.id
            }
        response = self.client.get('/api/grades/', filters)
        self.assertEqual(len(response.data), expected_grade_count)

    def test_num_queries(self):
        self.teacher_login()
        with self.assertNumQueries(1):
            self.client.get('/api/grades/')

    def test_ungraded_courses(self):
        """
        grades should not appear from courses that are "ungraded"
        """
        self.teacher_login()

        response = self.client.get('/api/grades/')
        all_grades = len(response.data)

        # change the first course to be non-graded
        self.data.course.graded = False
        self.data.course.save()

        response = self.client.get('/api/grades/')
        # should now be fewer grades
        self.assertLess(len(response.data), all_grades)

        # Now let's set it back and hopefully things work as expected again
        self.data.course.graded = True
        self.data.course.save()
        response = self.client.get('/api/grades/')
        self.assertEqual(len(response.data), all_grades)
'''
    def test_not_enrolled_student_grades(self):
        """
        grades should not be returned from non-enrolled students
        """
        self.teacher_login()

        response = self.client.get('/api/grades/')
        num_grades = len(response.data)

        # now get the enrollment associated with that first grade
        enrollment_instance = CourseEnrollment.objects.filter(user=self.data.student).first()
        enrollment_instance.is_active = False
        enrollment_instance.save()

        # let's figure out how many grades just became inactive!
        dead_grades = len(Grade.objects.filter(enrollment = enrollment_instance))

        # There should now be 1 less grade
        response = self.client.get('/api/grades/')
        new_num_grades = len(response.data)
        self.assertEqual(new_num_grades, num_grades - dead_grades)
'''











