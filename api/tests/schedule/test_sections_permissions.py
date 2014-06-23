from api.tests.api_test_base import APITest

class CourseSectionsAPIPermissionsTests(APITest):
    """
    test the permissions on get/posts requests to the course section API
    """
    def test_get_request_for_simple_permissions(self):
        """
        test a simple get request with both auth'd and non-auth'd users
        """
        # try it with a no authentication
        response = self.client.get('/api/sections/')
        self.assertEqual(response.status_code, 403)

        # try it with student authentication 
        self.client.force_authenticate(user = self.data.student)
        response = self.client.get('/api/sections/')
        self.assertEqual(response.status_code, 403)

        # try it with teacher authentication
        self.client.force_authenticate(user = self.data.teacher1)
        response = self.client.get('/api/sections/')
        self.assertEqual(response.status_code, 200)

    def test_get_request_for_specific_section(self):
        """
        permissions should be working for a request of a specific section
        """
        # try it with a no authentication
        response = self.client.get('/api/sections/1/')
        self.assertEqual(response.status_code, 403)

        # try it with student authentication 
        self.client.force_authenticate(user = self.data.student)
        response = self.client.get('/api/sections/')
        self.assertEqual(response.status_code, 403)

        # try it with teacher authentication
        self.client.force_authenticate(user = self.data.teacher1)
        response = self.client.get('/api/sections/1/')
        self.assertEqual(response.status_code, 200)

    def test_post_request_for_simple_permissions(self):
        """
        test a simple post request with both auth'd and non-auth'd users
        """
        data = {'course_id': 1, 'name': 'Math C', }

         # try it with a no authentication
        response = self.client.post('/api/sections/', data=data)
        self.assertEqual(response.status_code, 403)

        # try it with student authentication 
        self.client.force_authenticate(user = self.data.student)
        response = self.client.get('/api/sections/')
        self.assertEqual(response.status_code, 403)

        # try it with teacher authentication
        self.client.force_authenticate(user = self.data.teacher1)
        response = self.client.post('/api/sections/', data=data)
        self.assertEqual(response.status_code, 201)

    def test_put_request_for_simple_permissions(self):
        """
        test a simple put request with both auth'd and non-auth'd users
        """
        data = {'course_id': 1, 'name' : 'Math A - Modified'}

        # try it with a no authentication
        response = self.client.put('/api/sections/1/', data=data)
        self.assertEqual(response.status_code, 403)

        # try it with student authentication 
        self.client.force_authenticate(user = self.data.student)
        response = self.client.get('/api/sections/')
        self.assertEqual(response.status_code, 403)

        # try it with teacher authentication
        self.client.force_authenticate(user = self.data.teacher1)
        response = self.client.put('/api/sections/1/', data=data)
        self.assertEqual(response.status_code, 200)

    def test_delete_request_for_permissions(self):
        """
        obviously, only an admin should be able to delete a section!
        """
        # try it with a no authentication
        response = self.client.delete('/api/sections/1/')
        self.assertEqual(response.status_code, 403)

        # try it with student authentication 
        self.client.force_authenticate(user = self.data.student)
        response = self.client.get('/api/sections/')
        self.assertEqual(response.status_code, 403)

        # try it with teacher authentication
        self.client.force_authenticate(user = self.data.teacher1)
        response = self.client.delete('/api/sections/1/')
        self.assertEqual(response.status_code, 204)







