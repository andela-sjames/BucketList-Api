'''Script Used for authentication in Api Accesspoint. '''

from Flask_api import app, auth, db
from .models import User
from .errors import bad_request,unauthorized
from flask import request, jsonify, g, url_for


@app.route('/auth/login', methods=['POST'])
def new_user():

    '''User is registered and logged in. '''

    username = request.json.get('username')
    password = request.json.get('password')
    if not username  or not password:
        return bad_request('Missing arguments/parameters given')
    exist = User.query.filter_by(username=username).first()
    if not exist:
        user = User(username=username)
        user.hash_password(password)
        user.LoggedIn=True
        db.session.add(user)
        db.session.commit()
        return (jsonify({ 'user':user.to_json(),
                            'request_token':url_for('request_token'), 
                            'User':url_for('get_user', username = user.username,  _external =True) }),201)

    if exist.username and not exist.LoggedIn:
        exist.LoggedIn= True
        return (jsonify({ 'user':exist.to_json(),
                        'request_token':url_for('request_token'), 
                        'User':url_for('get_user', username = exist.username,  _external =True) }),201)
    else:
        if exist.username and exist.LoggedIn:
            return bad_request('User already exists and LoggedIn')


@app.route('/auth/logout/<username>', methods=['GET'])
@auth.login_required
def logout(username):

    ''' User is logged out and LoggedIn set to false.'''

    user = User.query.filter_by(username=username).first()
    if not user:
        return unauthorized('This account does not belong to you')
    user.LoggedIn = False
    db.session.add(user)
    db.session.commit()

    return jsonify({ 'message': 'You have successfully loggedOut',
            'Log-In':url_for('new_user', _external=True)})


@app.route('/auth/token')
@auth.login_required
def request_token():

    ''' User is given a token '''

    token = g.user.generate_auth_token()
    return jsonify({ 'token': token.decode('ascii')})


@app.route('/user/<username>')
@auth.login_required
def get_user(username):
    
    ''' Returns a user by username '''

    user = User.query.filter_by(username=username).first()
    if not user:
        return unauthorized()
    return jsonify({'user': user.to_json()})
