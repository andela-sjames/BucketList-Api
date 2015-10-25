import os
import datetime
from flask import Flask, abort, request, jsonify, g, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask.ext.httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)



app = Flask(__name__)

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