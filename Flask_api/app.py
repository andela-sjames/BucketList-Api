########################## CONFIGURATIONS AND SETTINGS #################

import os
import datetime
from flask import Flask, abort, request, jsonify, g, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask.ext.httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
#from flask_marshmallow import Marshmallow
from collections import OrderedDict
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
#from Flask_api.errors import bad_request
########################################################

#The import statements are:

########################################################

# initialization
app = Flask(__name__)
#ma = Marshmallow(app)

app.config['SECRET_KEY'] = 'qwertyuiop'
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://Administrator:administrator@localhost/bucketlist'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['PERPAGE_MIN_LIMIT'] = 20
app.config['PERPAGE_MAX_LIMIT'] = 100

#postgresql://Administrator:administrator@localhost/bucketlist

# extensions
db = SQLAlchemy(app)
auth = HTTPBasicAuth()
#####################################################

# initialize the 'CLI facing' flask extensions on the created app:

manager = Manager(app)
migrate = Migrate(app, db)

# add the flask-script commands to be run from the CLI:---to remove later
manager.add_command('db', MigrateCommand)

@manager.command
def test():
   """Discovers and runs unit tests"""
   import unittest
   tests = unittest.TestLoader().discover('tests')
   unittest.TextTestRunner(verbosity=2).run(tests)

################### MODELS  #######################
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    password_hash = db.Column(db.String(128))
    date_created = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    bucket = db.relationship('BucketList', backref='owner', lazy='dynamic')


    def to_json(self):

        return {
            "id": self.id,
            "username": self.username,
            "date_created": self.date_created.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def __repr__(self):
        return "<User(username='%s', email='%s')>" % (self.username,
         self.email)

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=42000):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None    # valid token, but expired
        except BadSignature:
            return None    # invalid token
        user = User.query.get(data['id'])
        return user


class BucketList(db.Model):
    __tablename__ = 'Bucketlists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    date_created = db.Column(db.DateTime, default=datetime.datetime.now())
    date_modified = db.Column(db.DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.utcnow())   
    created_by = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    items = db.relationship('Item', backref='bucketlist', cascade="all, delete-orphan",lazy='dynamic')


    #method to be defined here...
    #"items": [row.to_json() for row in self.items],
    def to_json(self):
        """Converts model object into dict to ease Serialization
        """
        return {
            "id": self.id,
            "name": self.name,
            "items_count": len(self.items.all()),
            "date_created": self.date_created.strftime("%Y-%m-%d %H:%M:%S"),
            "date_modified": self.date_modified.strftime("%Y-%m-%d %H:%M:%S"),
            "created_by": self.created_by,
        }



class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text(64))
    date_created = db.Column(db.DateTime,  default=datetime.datetime.utcnow())
    date_modified = db.Column(db.DateTime, default=datetime.datetime.utcnow(), onupdate=datetime.datetime.utcnow())   
    done = db.Column(db.Boolean, default=False) 

    bucketlist_id = db.Column(db.Integer, db.ForeignKey('Bucketlists.id'), nullable=False)
    


    def to_json(self):
        """Converts model object into dict to ease Serialization
        """
        return {
            "id": self.id,
            "name": self.name,
            "date_created": self.date_created.strftime("%Y-%m-%d %H:%M:%S"),
            "date_modified": self.date_modified.strftime("%Y-%m-%d %H:%M:%S"),
            "done": self.done,
        }



###################### ERRORS #######################
def not_found(message):
    response = jsonify({'status': 404, 'error': 'not found',
                        'message': message})
    response.status_code = 404
    return response

def bad_request(message):
    response = jsonify({'status': 400, 'error': 'bad request',
                        'message': message})
    response.status_code = 400
    return response

def precondition_failed():
    response = jsonify({'status': 412, 'error': 'precondition failed'})
    response.status_code = 412
    return response

###################### GLOBAL METHODS ##############################

@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


def jboolify(d):
    if d.done == True:
        d.done = 'true'
    else:
        d.done = 'false'
    return d

##################  API ACCESS POINTS HERE  #############################



###################### NEW API END POINT ############################
@app.route('/auth/login', methods=['POST'])
def new_user():
    username = request.json.get('username', ' ')
    password = request.json.get('password', ' ')
    if not username  or not password:
        return bad_request('Missing arguments/parameters given')
    if User.query.filter_by(username=username).first() is not None:
        return bad_request('User already exists')
    user = User(username=username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    user = User.query.get(user.id)
    #user.to_json()
    token = user.generate_auth_token(450000)
    return (jsonify({'user': user.to_json(), 'token': token.decode('ascii'), 'duration': 'expires on user logout' }), 201)


@app.route("/bucketlists", methods=['GET','POST'])
@auth.login_required
def create_and_getbucketlist():

    page = request.args.get('page', 1, type=int)# get page
    limit = request.args.get('limit', app.config['PERPAGE_MIN_LIMIT'],type = int) #get limit
    limit = limit if limit <= app.config['PERPAGE_MAX_LIMIT'] else app.config['PERPAGE_MAX_LIMIT'] 

    q = request.args.get('q')  #get q search value and use if available

    if request.method == 'GET':
        if q:
            alluserbucketlist = BucketList.query.filter_by(created_by=g.user.username).filter(BucketList.name.ilike('%{0}%'.format(q)))
        else:
            alluserbucketlist = BucketList.query.filter_by(created_by=g.user.username)
            
        if not alluserbucketlist:
            return jsonify({ 'message':'No bucketlist to display' })

        pagination = alluserbucketlist.paginate(page, per_page=limit, 
            error_out=False)
        buckets=pagination.items
        prev = None
        if pagination.has_prev:
            prev = url_for('create_and_getbucketlist', page=page-1,limit = 2, _external=True)
        next = None
        if pagination.has_next:
            next = url_for('create_and_getbucketlist', page=page+1,limit = limit, _external=True)
            
        return jsonify({
            'bucketlist': [bucket.to_json() for bucket in buckets], 
            'prev': prev,
            'next': next,
            'count': pagination.total
        })

    if request.method == 'POST':
        json_data = request.get_json()
        if not json_data['name']:
            return bad_request('No input data provided')

        bucketList = BucketList(name=json_data['name'],created_by=g.user.username, user_id=g.user.id)
        db.session.add(bucketList)
        db.session.commit()

        bucketid = BucketList.query.get(bucketList.id)
        return jsonify({'bucketlist':bucketid.to_json()})
        

@app.route("/bucketlists/<int:id>", methods=['GET', 'PUT', 'DELETE'])
@auth.login_required #get single bucketlist item
def get_delete_putbucketlist(id):

    bucketlist = BucketList.query.\
                filter_by(created_by=g.user.username).\
                filter_by(id=id).first()
    if not bucketlist:
            return not_found('bucket list with id:{} was not found' .format(id))

    page = request.args.get('page', 1, type=int)# get page
    limit = request.args.get('limit', app.config['PERPAGE_MIN_LIMIT'],type = int) #get limit
    limit = limit if limit <= app.config['PERPAGE_MAX_LIMIT'] else app.config['PERPAGE_MAX_LIMIT']

    if request.method == 'GET':

        if bucketlist:

            itemsquerydataset = bucketlist.items

            pagination =itemsquerydataset.paginate(page, per_page=limit, error_out=False)

            bucket_items=pagination.items

            prev = None
            if pagination.has_prev:
                prev = url_for('get_delete_putbucketlist', page=page-1, limit = limit, _external=True)
            next = None
            if pagination.has_next:
                next = url_for('get_delete_putbucketlist', page=page+1,limit = limit, _external=True)
            
            buckets=bucketlist.to_json()
            buckets['items'] = [ itemsqueryset.to_json() for itemsqueryset in bucket_items ]

            return jsonify({
                'bucketlist': buckets, 
                'prev': prev,
                'next': next,
                'count': pagination.total
            })

        
    if request.method == 'PUT':
        
        if bucketlist:
            json_data = request.get_json()
            bucketlist.name=json_data['name']
            db.session.add(bucketlist)
            db.session.commit()
            bucket=BucketList.query.get(id)

            return jsonify({'bucketlist':bucketlist.to_json()})

        
    if request.method == 'DELETE':

        if bucketlist:
            db.session.add(bucketlist)
            db.session.delete(bucketlist)
            db.session.commit()

            return jsonify({'message': 'bucketlist successfully deleted'})

        

@app.route("/bucketlists/<int:id>/items", methods=['POST'])
@auth.login_required #create item in bucketlist
def addnew_bucketlistitem(id):

    bucketlist = BucketList.query.\
                filter_by(created_by=g.user.username).\
                filter_by(id=id).first()

    if not bucketlist:
        return bad_request('bucket list with id:{} was not found' .format(id))

    json_data = request.get_json()
    if not json_data:
        return bad_request('No or incomplete input data provided')
    
    name, done = json_data['name'], json_data['done']    
    if done == 'TRUE' or 'true':        
        item = Item(name=name, done=True)
    else:
        item =Item(name=name,done=False)
        
    item.bucketlist_id=bucketlist.id
    db.session.add(item)
    db.session.commit()
    
    added_item=Item.query.get(item.id)
    return jsonify({'Item':added_item.to_json()})

@app.route("/bucketlists/<int:id>/items/<int:item_id>", methods=['PUT', 'DELETE'])
@auth.login_required
def delete_and_update(id, item_id):

    
    bucketlist = BucketList.query.\
                filter_by(created_by=g.user.username).\
                filter_by(id=id).first()
    if not bucketlist:
        return bad_request('bucket list with id:{} was not found' .format(id))
    
    item =Item.query.get(item_id)
    if not item:
            return bad_request('bucket list with id:{} was not found' .format(item_id))

    if request.method == 'PUT':
        if item:
            if item.bucketlist_id == bucketlist.id:
                json_data = request.get_json()
                name, done = json_data['name'], json_data['done']
        
                if done == 'TRUE' or 'true':        
                    item = Item(name=name, done=True)
                else:
                    item =Item(name=name,done=False)

                item.bucketlist_id=bucketlist.id
                db.session.add(item)
                db.session.commit()

                responseitem = jboolify(Item.query.get(item.id))
                return jsonify({'Item':responseitem.to_json()})
        else:
            return bad_request('item not related to bucketlist')

    if request.method == 'DELETE':
        if item:

            db.session.add(item)
            db.session.delete(item)
            db.session.commit()

        return jsonify({'message': 'bucketlist successfully deleted'})


###################### RUN ################################

if __name__ == '__main__':
    manager.run()
