import os, json
import unittest
from Flask_api import app, db
from base64 import b64encode 
from Flask_api.models import BucketList, Item, User
from flask import url_for, g

basedir = os.path.abspath(os.path.dirname(__file__))

class APITestCase(unittest.TestCase):

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
        u.save()
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

class ItemsTestCase(APITestCase): 

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

if __name__ == '__main__':
    unittest.main()
