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
from flask_marshmallow import Marshmallow
from collections import OrderedDict
#from Flask_api.errors import bad_request


# initialization
app = Flask(__name__)
ma = Marshmallow(app)

app.config['SECRET_KEY'] = 'qwertyuiop'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bucket.sqlite'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

# extensions
db = SQLAlchemy(app)
auth = HTTPBasicAuth()

################### MODELS  #######################
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    password_hash = db.Column(db.String(128))
    date_created = db.Column(db.DateTime, default=datetime.datetime.now())


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
    date_modified = db.Column(db.DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())   
    created_by = db.Column(db.String(64))



class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    date_created = db.Column(db.DateTime,  default=datetime.datetime.now())
    date_modified = db.Column(db.DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())   
    done = db.Column(db.Boolean, default=False) 

    bucketlist_id = db.Column(db.Integer, db.ForeignKey('Bucketlists.id'))
    bucketlist = db.relationship('BucketList', backref=db.backref('items', lazy='dynamic'))
############### SCHEMA #############################

class UserSchema(ma.Schema):

    class Meta:
        # Fields to expose
        fields = ('id', 'username','date_created')
        #ordered = True
        

class BucketListSchema(ma.Schema):
    
    class Meta:

        fields = ('id', 'name','items', 'date_created', 'date_modified', 'created_by')
        #ordered = True
        
class ItemSchema(ma.Schema):
    
    class Meta:

        done = ma.Boolean(attribute='done', missing=False)
        bucketlist=ma.Nested(BucketListSchema, many=True)
        fields = ('id', 'name', 'bucketlist','date_created', 'date_modified', 'done')
        #ordered = True    



user_schema = UserSchema()
users_schema = UserSchema(many=True)
list_schema = BucketListSchema()
lists_schema = BucketListSchema(many = True)
item_schema = ItemSchema()
items_schema = ItemSchema(many = True)
################### NEW API ENTRY POINT ##################








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


##################  API ACCESS POINTS HERE  #############################



###################### NEW API END POINT ############################
@app.route('/auth/login', methods=['POST'])
def new_user():
    username = request.json.get('username', ' ')
    password = request.json.get('password', ' ')
    if username is None or password is None:
        return bad_request('Missing arguments/parameters given')
    if User.query.filter_by(username=username).first() is not None:
        return bad_request('User already exists')
    user = User(username=username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    user = User.query.get(user.id)
    result = user_schema.dump(user)
    token = user.generate_auth_token(450000)
    return (jsonify({'user': result.data, 'token': token.decode('ascii'), 'duration': 'expires on user logout' }), 201)



@app.route("/bucketlists", methods=['GET','POST'])
def create_and_getbucketlist():

    if request.method == 'GET':

        bucketlist = BucketList.query.get.all()
        Bucketlist_result = lists_schema.dump(bucketlists)
        item_result=item_schema.dump(bucketlist.items.all())
        return jsonify({'Bucketlist':Bucketlist_result.data, 'items': item_result.data })


    if request.method == 'POST':

        json_data = request.get_json()
        if not json_data['name']:
            return bad_request('No input data provided')

        bucketList = BucketList(name=json_data['name'],created_by=g.user.username)
        db.session.add(bucketList)
        db.session.commit()
        bucketid=BucketList.query.get(bucketList.id)
        Bucketlist_result = lists_schema.dump(bucketid)
        item_result=item_schema.dump(bucketlist.items.all())
        return jsonify({'Bucketlist':Bucketlist_result.data, 'items': item_result.data })


@app.route("/bucketlists/<id>", methods=['GET', 'PUT', 'DELETE'])#get single bucketlist item
def get_delete_putbucketlist(id):

    if request.method == 'GET':
        try:
            bucketlist = BucketList.query.get(id)
        except IntegrityError:
            return not_found('bucket list with id:{} was not found' .format(id))
        Bucketlist_result = list_schema.dump(bucketlist)
        item_result=item_schema.dump(bucketlist.items.all())
        return jsonify({'Bucketlist':Bucketlist_result.data, 'items': item_result.data })

    if request.method == 'PUT':

        try:
            bucketlist = BucketList.query.get(id)
        except IntegrityError:
            return not_found('bucket list with id:{} was not found' .format(id))

        bucketlist.name=json_data['name']
        db.session.add(bucketlist)
        db.session.commit()
        bucket=BucketList.query.get(id)

        Bucketlist_result = list_schema.dump(bucket)
        item_result=item_schema.dump(bucket.items.all())
        return jsonify({'Bucketlist':Bucketlist_result.data, 'items': item_result.data })

    if request.method == 'DELETE':

        try:
            bucketlist = BucketList.query.get(id)
        except IntegrityError:
            return not_found('bucket list already deleted')

        db.session.add(bucketlist)
        db.session.add(bucketlist.items.all())
        db.session.delete(bucketlist)
        db.session.delete(bucketlist.items.all())
        db.session.commit()

        return jsonify({'message': 'bucketlist has successfully been deleted'})


@app.route("/bucketlists/<id>/items", methods=["POST"])#create item in bucketlist
def new_item(id):
    json_data = request.get_json()
    if not json_data:
        return bad_request('No or incomplete input data provided')
    
    bucketlist = BucketList.query.get(id)
    if not bucketlist:
        return bad_request('bucket list with id:{} was not found' .format(id))

    db.session.add(bucketlist)

    #create new item
    name = json_data['name']
    done = True if json_data['done'] == 'true' or 'True' or 'TRUE' else False
    item = Item(name =name,done=done)

    db.session.add(item)
    db.session.commit()

    result = item_schema.dump(Item.query.get(item.id))
    return jsonify({"message": "Created new item.",
                    "items": result.data})


        
###############################################################
@app.route('/auth/users/<int:id>')
def get_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'username': user.username, 'date_created': user.date_created })


@app.route('/auth/token', methods=['POST'])
#@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(3600)
    return jsonify({'token': token.decode('ascii'), 'duration': 3600})

###################### RUN ################################

if __name__ == '__main__':
    if not os.path.exists('db.sqlite'):
        db.create_all()
    app.run(debug=True)
