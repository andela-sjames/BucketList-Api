import os, json
import unittest
from Flask_api import app, db
from base64 import b64encode 
from Flask_api.models import BucketList, Item, User
from flask import url_for, g

basedir = os.path.abspath(os.path.dirname(__file__))
#headers = {'Authorization': 'Basic ' + b64encode("{0}:{1}".format(username, password))}

class APIClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
        app.config['SERVER_NAME'] = 'localhost'
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = app.test_client()
        u = User(username='James')
        u.hash_password('Andela')
        u.LoggedIn = True
        db.session.add(u)
        db.session.commit()
        g.user = u                
        
    def tearDown(self):
        db.session.remove() 
        db.drop_all() 
        self.app_context.pop()

    def get_api_headers(self, username, password):
        return {
            'Authorization':
                'Basic ' + b64encode(
                    (username + ':' + password).encode('utf-8')).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

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


    def test_bucketlists(self):

        ''' Test User can create and get bucketlist'''

        #POST create 2 bucketlist
        response = self.client.post(
            url_for('create_and_getbucketlist'),
            headers=self.get_api_headers('James', 'Andela'),
            data=json.dumps({'name': 'I just created a bucketlist'}))
        self.assertTrue(response.status_code == 200)

        response = self.client.post(
            url_for('create_and_getbucketlist'),
            headers=self.get_api_headers('James', 'Andela'),
            data=json.dumps({'name': 'I just created another'}))
        self.assertTrue(response.status_code == 200)

        #get all bucketlists
        response = self.client.get(
            url_for('create_and_getbucketlist'),
            headers=self.get_api_headers('James', 'Andela'))

        self.assertTrue(response.status_code == 200)

        #get buckelist via search parameter
        response = self.client.get(
            url_for('create_and_getbucketlist', q ='create'),
            headers=self.get_api_headers('James', 'Andela'))

        self.assertTrue(response.status_code == 200)

        #get bucketlist via limit
        response = self.client.get(
            url_for('create_and_getbucketlist', limit =1, page =1),
            headers=self.get_api_headers('James', 'Andela'))

        self.assertTrue(response.status_code == 200)

    def test_bucketlist_id(self):

        ''' Test User can query via bucketlist id.'''

        #create 2 bucketlist
        response = self.client.post(
            url_for('create_and_getbucketlist'),
            headers=self.get_api_headers('James', 'Andela'),
            data=json.dumps({'name': 'I just created a bucketlist'}))
        self.assertTrue(response.status_code == 200)

        response = self.client.post(
            url_for('create_and_getbucketlist'),
            headers=self.get_api_headers('James', 'Andela'),
            data=json.dumps({'name': 'I just created another'}))
        self.assertTrue(response.status_code == 200)

        #GET bucketlist via id
        response = self.client.get(
            url_for('get_delete_putbucketlist', id =1 ),
            headers=self.get_api_headers('James', 'Andela'))
        self.assertTrue(response.status_code == 200)

        #get bucketlist via limit and page
        response = self.client.get(
            url_for('get_delete_putbucketlist', id =1, limit = 1, page =1 ),
            headers=self.get_api_headers('James', 'Andela'))
        self.assertTrue(response.status_code == 200)

        #get non user bucketlist via id
        response = self.client.get(
            url_for('get_delete_putbucketlist', id =9),
            headers=self.get_api_headers('James', 'Andela'))
        self.assertTrue(response.status_code == 405)


        #user can't post to others bucketlist
        response = self.client.post(
            url_for('get_delete_putbucketlist', id =5 ),
            headers=self.get_api_headers('James', 'Andela'))
        self.assertTrue(response.status_code == 405)


        #PUT update bucketlist via id
        response = self.client.put(
            url_for('get_delete_putbucketlist', id =1),
            headers=self.get_api_headers('James', 'Andela'),
            data=json.dumps({'name': 'Another reason to code'}))
        self.assertTrue(response.status_code == 200)

        #DELETE delete bucketlist via id
        response = self.client.delete(
        url_for('get_delete_putbucketlist', id =1 ),
            headers=self.get_api_headers('James', 'Andela'))
        self.assertTrue(response.status_code == 200)

    def test_add_bucketitems(self):

        '''Test that user can post data to bucket items. '''

        #create a bucketlist
        response = self.client.post(
            url_for('create_and_getbucketlist'),
            headers=self.get_api_headers('James', 'Andela'),
            data=json.dumps({'name': 'I just created a bucketlist'}))
        self.assertTrue(response.status_code == 200)

        #create 2 bucketlist items.
        response = self.client.post(
            url_for('addnew_bucketlistitem', id = 1),
            headers=self.get_api_headers('James', 'Andela'),
            data=json.dumps({'name': 'Flask api', 'done': True }))
        self.assertTrue(response.status_code == 200)

        response = self.client.post(
            url_for('addnew_bucketlistitem', id = 1),
            headers=self.get_api_headers('James', 'Andela'),
            data=json.dumps({'name': 'Django api', 'done': False }))
        self.assertTrue(response.status_code == 200)

        #create a wrong bucketlist item
        response = self.client.post(
            url_for('addnew_bucketlistitem', id = 5),
            headers=self.get_api_headers('James', 'Andela'),
            data=json.dumps({'name': 'Flask api', 'done': True }))
        self.assertTrue(response.status_code == 400)

        #search for a non-user bucketlist
        response = self.client.get(
            url_for('addnew_bucketlistitem', id = 4),
            headers=self.get_api_headers('James', 'Andela'))
        self.assertTrue(response.status_code == 405)



    def test_bucketlist_items(self):

        ''' Test that user can put and delete items.'''

        #create a bucketlist
        response = self.client.post(
            url_for('create_and_getbucketlist'),
            headers=self.get_api_headers('James', 'Andela'),
            data=json.dumps({'name': 'I just created a bucketlist'}))
        self.assertTrue(response.status_code == 200)

        #send empty data to bucketlist item
        response = self.client.post(
            url_for('addnew_bucketlistitem', id = 1),
            headers=self.get_api_headers('James', 'Andela'),
            data=json.dumps({'name': ' ', 'done':''}))
        self.assertTrue(response.status_code == 200)

        #create a bucketlist item.
        response = self.client.post(
            url_for('addnew_bucketlistitem', id = 1),
            headers=self.get_api_headers('James', 'Andela'),
            data=json.dumps({'name': 'Flask api', 'done': True }))
        self.assertTrue(response.status_code == 200)

        #update the buckelistitem
        response = self.client.put(
            url_for('delete_and_update', id = 1, item_id = 1),
            headers=self.get_api_headers('James', 'Andela'),
            data=json.dumps({'name': 'RESTful api', 'done': True }))
        self.assertTrue(response.status_code == 200)

        #update the wrong bucktlistiem
        response = self.client.put(
            url_for('delete_and_update', id = 1, item_id = 3),
            headers=self.get_api_headers('James', 'Andela'),
            data=json.dumps({'name': 'RESTful api', 'done': True }))
        self.assertTrue(response.status_code == 400)
        #update the wrong list
        response = self.client.put(
            url_for('delete_and_update', id = 2, item_id = 2),
            headers=self.get_api_headers('James', 'Andela'),
            data=json.dumps({'name': 'RESTful api'}))
        self.assertTrue(response.status_code == 400)

        #delete the bucketlist item
        response = self.client.delete(
            url_for('delete_and_update', id = 1, item_id = 1),
            headers=self.get_api_headers('James', 'Andela'))
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