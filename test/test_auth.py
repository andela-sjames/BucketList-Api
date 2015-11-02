import os, json
from Flask_api import db 
from Flask_api.models import User
from flask import url_for, g
from . test_bucketlistitem import APITestCase

class APIAuthTestCase(APITestCase):

    '''Class defined to test user authentication.'''

    def test_auth_login(self):

        ''' Test User can login'''

        #user logs in 
        user={'username': 'general', 'password': 'James'}
        response = self.client.post(
            '/auth/login',
            content_type='application/json',
            data=json.dumps(user),
            )
        self.assertEqual(response.status_code, 201, msg='response status should be 201')

        #test user data not entered
        user={'username': '', 'password': ''}
        response = self.client.post(
            '/auth/login',
            content_type='application/json',
            data=json.dumps(user),
            )
        self.assertEqual(response.status_code, 400, msg='response status should be 400, missing data')

        #test already existing user can get new token
        user={'username': 'James','password':'Andela'}
        response = self.client.post(
            '/auth/login',
            content_type='application/json',
            data=json.dumps(user),
            )
        self.assertEqual(response.status_code, 201, msg='response status should be 400 user already exists')

        #test user password validation
        user={'username': 'James','password':'mandela'}
        response = self.client.post(
            '/auth/login',
            content_type='application/json',
            data=json.dumps(user),
            )
        self.assertEqual(response.status_code, 401, msg='response status should be 400 user already exists')

        
        #test user can view self info
        response = self.client.get(
            url_for('get_user', username = 'James'),
            headers=self.get_api_headers('James', 'Andela'))

        self.assertTrue(response.status_code == 200)

        #test user can't view another user data
        response = self.client.get(
            url_for('get_user', username = 'mathew'),
            headers=self.get_api_headers('James', 'Andela'))
        #import pdb; pdb.set_trace()

        self.assertTrue(response.status_code == 401)
        
    def test_token_auth(self):

        #user signs up and gets token
        user={'username': 'general', 'password': 'James'}
        response = self.client.post(
            '/auth/login',
            content_type='application/json',
            data=json.dumps(user),
            )
        self.assertEqual(response.status_code, 201, msg='response status should be 201')
        json_response = json.loads(response.data.decode('utf-8'))
        token = json_response['token']

        #issue a request with the token
        response = self.client.get(
            url_for('create_and_getbucketlist'),
            headers=self.get_api_headers(token, ''))
        self.assertTrue(response.status_code == 200)


if __name__ == '__main__':
    unittest.main()

