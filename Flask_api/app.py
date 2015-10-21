import os
from flask import Flask, abort, request, jsonify, g, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from flask_marshmallow import Marshmallow
#from Flask_api.errors import bad_request


# initialization
app = Flask(__name__)
app.config['SECRET_KEY'] = 'qwertyuiopasdfghjklzxcvbnm'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

# extensions
ma = Marshmallow(app)
db = SQLAlchemy(app)
auth = HTTPBasicAuth()

####################################################################
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, unique=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(64))
    email = db.Column(db.String(32), unique=True)

    lists = db.relationship('List', backref='users', lazy='dynamic')

    def __repr__(self):
        return "<User(username='%s', email='%s')>" % (self.username,
         self.email)

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=3600):
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

#######################################################################
class List(db.Model):
    __tablename__ = 'lists'
    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String(32))
    date_created = db.Column(db.DateTime)
    date_modified = db.Column(db.DateTime)   
    created_by = db.Column(db.String(32))

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    items = db.relationship('Item', backref='lists', lazy='dynamic')



################################################################

class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String(32))
    date_created = db.Column(db.DateTime)
    date_modified = db.Column(db.DateTime)   
    done = db.Column(db.Boolean) 

    list_id = db.Column(db.Integer, db.ForeignKey('lists.id'))

##########################################################################

def bad_request(message):
    response = jsonify({'status': 400, 'error': 'bad request',
                        'message': message})
    response.status_code = 400
    return response


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



@app.route('/auth/login', methods=['POST'])
def new_user():
    username = request.form.get('username', ' ')
    password = request.form.get('password', ' ')
    if username is None or password is None:
        return bad_request('Missing arguments/parameters given')
    if User.query.filter_by(username=username).first() is not None:
        return bad_request('User already exists')
    user = User(username=username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return (jsonify({'username': user.username}), 201)




@app.route('/auth/users/<int:id>')
def get_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'username': user.username})


@app.route('/auth/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})



if __name__ == '__main__':
    if not os.path.exists('db.sqlite'):
        db.create_all()
    app.run(debug=True)
