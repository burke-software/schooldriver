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

        # try it with teacher authentication
        self.client.force_authenticate(user = self.data.teacher1)
        response = self.client.get('/api/grades/')
        self.assertEqual(response.status_code, 200)

        # try it with a student (who clearly has no authoritay)
        self.client.force_authenticate(user = self.data.student)
        response = self.client.get('/api/grades/')
        self.assertEqual(response.status_code, 403)

