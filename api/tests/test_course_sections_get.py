from api.tests.api_test_base import APITest

class CourseSectionAPIGetTests(APITest):
    """
    test the implementation of our course sections api with get requests
    """

    def test_sections_get_request_for_simple_permissions(self):
        """
        test a simple get request with both auth'd and non-auth'd users
        """

        # try it with a no authentication
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

        # try it with teacher authentication
        self.client.force_authenticate(user = self.data.teacher1)
        response = self.client.get('/api/sections/1/')
        self.assertEqual(response.status_code, 200)


    def test_sections_get_request(self):
        """
        the api should successfully return all pre-populated section data
        """
        self.client.force_authenticate(user = self.data.teacher1)
        response = self.client.get('/api/sections/')
        # there are 4 sections in the sample data
        self.assertEqual(len(response.data), 4)

    def test_data_returned_from_specific_get_request(self):
        """
        the api should successfully retun a specific section when asked
        """
        self.client.force_authenticate(user = self.data.teacher1)
        response = self.client.get('/api/sections/1/')
        self.assertEqual(response.data['name'], 'Math A')
        self.assertEqual(response.data['course']['fullname'], 'Math 101')

        # let's try another section just to be sure

        response = self.client.get('/api/sections/3/')
        self.assertEqual(response.data['name'], 'History A')
        self.assertEqual(response.data['course']['fullname'], 'History 101')






