import jwt
from functools import wraps
from datetime import datetime, timedelta
from flask import request, jsonify, g
from config.config import Config


def generate_token(user_id, role_id, role_name):
    payload = {
        'user_id': user_id,
        'role_id': role_id,
        'role_name': role_name,
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'message': 'Token is missing', 'success': False}), 401

        try:
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
            g.current_user_id = data['user_id']
            g.current_role_id = data['role_id']
            g.current_role_name = data['role_name']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired', 'success': False}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token', 'success': False}), 401

        return f(*args, **kwargs)

    return decorated


def admin_required(f):
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        if g.current_role_name != 'Admin':
            return jsonify({'message': 'Admin access required', 'success': False}), 403
        return f(*args, **kwargs)
    return decorated


def manager_or_admin_required(f):
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        if g.current_role_name not in ['Admin', 'Manager']:
            return jsonify({'message': 'Manager or Admin access required', 'success': False}), 403
        return f(*args, **kwargs)
    return decorated
