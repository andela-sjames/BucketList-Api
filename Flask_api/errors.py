

from flask import jsonify, url_for, current_app

def unauthorized(message=None):
    if message is None:
        if current_app.config['SECRET_KEY']:
            message = 'Please authenticate with your token.'
        else:
            message = 'Please authenticate.'
    response = jsonify({'status': 401, 'error': 'unauthorized',
                        'message': message, 
                        'authentication path':url_for('request_token')})
    response.status_code = 401
    if current_app.config['SECRET_KEY']:
        response.headers['Location'] = url_for('request_token')
    return response

def too_many_requests(message='You have exceeded your request rate'):
    response = jsonify({'status': 429, 'error': 'too many requests',
                        'message': message})
    response.status_code = 429
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
