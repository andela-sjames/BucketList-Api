

from flask import jsonify, url_for
from Flask_api import app

def unauthorized(message=None):
    if message is None:
        if app.config['SECRET_KEY']:
            message = 'Please authenticate with your token.'
        else:
            message = 'Please authenticate.'
    response = jsonify({'status': 401, 'error': 'unauthorized',
                        'message': message, 
                        'authentication path':url_for('request_token')})
    response.status_code = 401
    if app.config['SECRET_KEY']:
        response.headers['Location'] = url_for('request_token')
    return response

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
