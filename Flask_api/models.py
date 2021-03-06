''' Script used to define models for Api serveic.'''

from Flask_api import app, db, auth
from flask import g
from datetime import datetime
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from .errors import unauthorized

class Base(db.Model):

    ''' Abstract Base class used to define datetime and id.'''

    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime,index=True, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime,index=True, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # saves the data
    def save(self):
        db.session.add(self)
        db.session.commit()

    # deletes the data
    def delete(self):
        db.session.add(self)
        db.session.delete(self)
        db.session.commit()



class User(Base):

    '''User table defined for user authenticatin.'''

    __tablename__ = 'users'
    username = db.Column(db.String(64), index=True)
    password_hash = db.Column(db.String(128))
    LoggedIn = db.Column(db.Boolean, default=True)
    bucket = db.relationship('BucketList', backref='owner', lazy='dynamic')


    def to_json(self):

        ''' Method to convert objects to python dictioary format.'''

        return {
            "id": self.id,
            "username": self.username,
            "date_created": self.date_created.strftime("%Y-%m-%d %H:%M:%S"),
            "LoggedIn": self.LoggedIn
        }

    def __repr__(self):
        return "<User(username='%s', email='%s')>" % (self.username,
         self.email)

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=86400):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):

        '''Method to verify user token.'''

        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None   # valid token, but expired
        except BadSignature:
            return None    # invalid token
        g.user = User.query.get(data['id'])
        return g.user


class BucketList(Base):

    '''Bucketlist model defined'''

    __tablename__ = 'Bucketlists'
    name = db.Column(db.String(64))  
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_by = db.Column(db.String(64))
    items = db.relationship('Item', backref='bucketlist', cascade="all, delete-orphan",lazy='dynamic')

    def to_json(self):

        ''' Method to convert objects to python dictioary format.'''
        
        return {
            "id": self.id,
            "name": self.name,
            "items_count":len(self.items.all()),
            "date_created": self.date_created.strftime("%Y-%m-%d %H:%M:%S"),
            "date_modified": self.date_modified.strftime("%Y-%m-%d %H:%M:%S"),
            "created_by": self.created_by,
        }



class Item(Base):

    '''Item model defined for api service. '''

    __tablename__ = 'items'
    name = db.Column(db.String(64))   
    done = db.Column(db.Boolean, default=False, nullable =False) 
    bucketlist_id = db.Column(db.Integer, db.ForeignKey('Bucketlists.id'), nullable=False)
    


    def to_json(self):

        ''' Method to convert objects to python dictioary format.'''
        
        return {
            "id": self.id,
            "name": self.name,
            "date_created": self.date_created.strftime("%Y-%m-%d %H:%M:%S"),
            "date_modified": self.date_modified.strftime("%Y-%m-%d %H:%M:%S"),
            "done": self.done,
        }

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

@auth.error_handler
def unauthorized_error():
    return unauthorized()

