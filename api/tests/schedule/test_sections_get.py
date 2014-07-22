from api.tests.api_test_base import APITest

class CourseSectionAPIGetTests(APITest):
    """
    test the implementation of our course sections api with get requests
    """

    def test_sections_get_request(self):
        """
        the api should successfully return all pre-populated section data
        """
        self.teacher_login()
        response = self.client.get('/api/sections/')
        # there are 4 sections in the sample data
        self.assertEqual(len(response.data), 4)

    def test_data_returned_from_specific_get_request(self):
        """
        the api should successfully return a specific section when asked
        """
        self.teacher_login()
        response = self.client.get('/api/sections/1/')
        self.assertEqual(response.data['name'], 'Math A')
        self.assertEqual(response.data['course']['fullname'], 'Math 101')

        # let's try another section just to be sure
        response = self.client.get('/api/sections/3/')
        self.assertEqual(response.data['name'], 'History A')
        self.assertEqual(response.data['course']['fullname'], 'History 101')






