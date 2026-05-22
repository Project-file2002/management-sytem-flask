from flask import Blueprint, request, jsonify, g
from services.auth_service import AuthService
from middleware.auth_middleware import token_required

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided', 'success': False}), 400

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Email and password are required', 'success': False}), 400

    result = AuthService.login(email, password)
    if result['success']:
        return jsonify(result), 200
    return jsonify(result), 401


@auth_bp.route('/api/logout', methods=['POST'])
@token_required
def logout():
    return jsonify({'message': 'Logged out successfully', 'success': True}), 200


@auth_bp.route('/api/profile', methods=['GET'])
@token_required
def get_profile():
    result = AuthService.get_profile(g.current_user_id)
    if result['success']:
        return jsonify(result), 200
    return jsonify(result), 404


@auth_bp.route('/api/change-password', methods=['PUT'])
@token_required
def change_password():
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided', 'success': False}), 400

    current_password = data.get('current_password')
    new_password = data.get('new_password')

    if not current_password or not new_password:
        return jsonify({'message': 'Current and new password are required', 'success': False}), 400

    result = AuthService.change_password(g.current_user_id, current_password, new_password)
    if result['success']:
        return jsonify(result), 200
    return jsonify(result), 400
