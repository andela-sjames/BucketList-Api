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

        #test user already exist
        user={'username': 'James','password':'Andela'}
        response = self.client.post(
            '/auth/login',
            content_type='application/json',
            data=json.dumps(user),
            )
        self.assertEqual(response.status_code, 400, msg='response status should be 400 user already exists')
        
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
        # add a user
        user = User.query.filter_by(username='Gentle').first()
        self.assertIsNone(user)
        user = User(username='Gentle')
        user.hash_password('fella')
        db.session.add(user)
        db.session.commit()
        g = user

        # issue a request with a bad token
        response = self.client.get(
            url_for('request_token'),
            headers=self.get_api_headers('bad-token', ''))
        self.assertTrue(response.status_code == 401)

        #get a token
        response = self.client.get(
            url_for('request_token'),
            headers=self.get_api_headers('Gentle', 'fella'))
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertIsNotNone(json_response.get('token'))
        token = json_response['token']

        #issue a request with the token
        response = self.client.get(
            url_for('request_token'),
            headers=self.get_api_headers(token, ''))
        self.assertTrue(response.status_code == 200)

    def test_user_logout(self):

        ''' Test that user can logout and login'''

        #user logs in
        user={'username': 'general', 'password': 'James'}
        response = self.client.post(
            '/auth/login',
            content_type='application/json',
            data=json.dumps(user),
            )
        self.assertEqual(response.status_code, 201, msg='response status should be 201')

        #user logs in again without logging out.
        user={'username': 'general', 'password': 'James'}
        response = self.client.post(
            '/auth/login',
            content_type='application/json',
            data=json.dumps(user),
            )
        self.assertEqual(response.status_code, 400, msg='response status should be 400 user already exist and LoggedIn')

        #user logs out
        response = self.client.get(
            url_for('logout', username='general'),
            headers=self.get_api_headers('general', 'James'))
        self.assertTrue(response.status_code == 200)

        #user should not logout an existing user.
        response = self.client.get(
            url_for('logout', username='James'),
            headers=self.get_api_headers('general', 'James'))
        self.assertTrue(response.status_code == 401)

        #user logs in again
        user={'username': 'general', 'password': 'James'}
        response = self.client.post(
            '/auth/login',
            content_type='application/json',
            data=json.dumps(user),
            )
        self.assertEqual(response.status_code, 201, msg='response status should be 201')


if __name__ == '__main__':
    unittest.main()

