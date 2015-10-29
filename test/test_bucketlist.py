import os, json
import unittest
from Flask_api import app, db
from base64 import b64encode 
from Flask_api.models import BucketList, Item, User
from flask import url_for, g

basedir = os.path.abspath(os.path.dirname(__file__))

class APIBucketlistTestCase(unittest.TestCase):

    def setUp(self):

        '''Instanciate test.'''

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

        '''Teardown testcase'''

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

if __name__ == '__main__':
    unittest.main()