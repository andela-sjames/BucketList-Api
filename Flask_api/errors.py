''' Script used to define servEral and various errors on api.'''

from flask import jsonify, url_for
from Flask_api import app

def unauthorized(message=None):

    ''' User is unauthorised to perform action.'''

    if message is None:
        if app.config['SECRET_KEY']:
            message = 'Please authenticate with your token.'
        else:
            message = 'Please authenticate.'
    response = jsonify({'status': 401, 'error': 'unauthorized',
                        'message': message})
    response.status_code = 401
    if app.config['SECRET_KEY']:
        response.headers['Location'] = url_for('new_user')
    return response

def bad_request(message):

    '''Request is bad and not valid '''

    response = jsonify({'status': 400, 'error': 'bad request',
                        'message': message})
    response.status_code = 400
    return response

def not_allowed():

    '''Method not allowed'''

    response = jsonify({'status': 405, 'error': 'method not allowed'})
    response.status_code = 405
    return response
