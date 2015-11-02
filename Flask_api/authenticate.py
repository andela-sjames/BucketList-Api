'''Script Used for authentication in Api Accesspoint. '''

from Flask_api import app, auth, db
from .models import User
from .errors import bad_request,unauthorized
from flask import request, jsonify, g, url_for


@app.route('/auth/login', methods=['POST'])
def new_user():
    username = request.json.get('username', ' ')
    password = request.json.get('password', ' ')


    if not username  or not password:
        return bad_request('Missing arguments/parameters given')

    exist = User.query.filter_by(username=username).first()

    if not exist:
        user = User(username=username)
        user.hash_password(password)
        user.save()
        user = User.query.get(user.id)
        token = user.generate_auth_token()

        return (jsonify({'user': user.to_json(), 
            'token': token.decode('ascii'), 
            'duration': 'expires after 24 hours',
            'User':url_for('get_user', username = user.username,  _external =True) }), 201)

    if exist.username and not exist.verify_password(password):
        return unauthorized('Incorrect password entered, please confirm')

    if exist.username and exist.verify_password(password):
        
        token = exist.generate_auth_token()
        return (jsonify({ 'user':exist.to_json(),
                    'token': token.decode('ascii'),
                    'duration': 'expires after 24 hours'}), 201)


@app.route('/user/<username>')
@auth.login_required
def get_user(username):
    
    ''' Returns a user by username '''

    user = User.query.filter_by(username=username).first()
    if not user:
        return unauthorized()
    return jsonify({'user': user.to_json()})
