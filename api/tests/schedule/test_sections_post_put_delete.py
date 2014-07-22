from api.tests.api_test_base import APITest

class CourseSectionAPIPostTests(APITest):
    """
    test implementation of our course sections api with post/delete requests
    """

    def test_post_request_for_new_section(self):
        """
        a post request should populate the database with a new section
        """
        self.teacher_login()

        # get the current number of sections
        response = self.client.get('/api/sections/')
        original_number = len(response.data)

        # create a new section and post it
        data = {'course_id': 1, 'name': 'Math C', }
        response = self.client.post('/api/sections/', data=data)
        self.assertEqual(response.status_code, 201)

        # now, make sure it was added to the sections list
        response = self.client.get('/api/sections/')
        self.assertEqual(original_number+1, len(response.data))

    def test_delete_request(self):
        """
        a delete request should remove a section from the database
        """
        self.teacher_login()
        # get the current number of sections
        response = self.client.get('/api/sections/')
        original_number = len(response.data)

        # delete one of them
        self.client.delete('/api/sections/1/')

        # make sure it's actually gone
        response = self.client.get('/api/sections/')
        self.assertEqual(original_number-1, len(response.data))

    def test_put_request_to_modify_a_section(self):
        """
        a put request to an existing section should modify the section
        """
        # change the name of an existing section
        self.teacher_login()
        data = {'course_id': 1, 'name': 'Waka Waka!!!'}
        response = self.client.put('/api/sections/1/', data = data)

        # make sure the changes took
        response = self.client.get('/api/sections/1/')
        self.assertEqual(response.data['name'], 'Waka Waka!!!')

    def test_post_request_without_post_data(self):
        """
        a post request without any data should return an error
        """
        self.teacher_login()
        response = self.client.post('/api/sections/')
        self.assertIn('This field is required', response.data['name'][0])
        self.assertIn('This field is required', response.data['course_id'][0])
        self.assertEqual(response.status_code, 400)





