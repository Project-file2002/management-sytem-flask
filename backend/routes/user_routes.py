from flask import Blueprint, request, jsonify, g
from services.user_service import UserService
from middleware.auth_middleware import admin_required, token_required

user_bp = Blueprint('users', __name__)


@user_bp.route('/api/users', methods=['GET'])
@admin_required
def get_users():
    result = UserService.get_all_users()
    return jsonify(result), 200 if result['success'] else 500


@user_bp.route('/api/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    result = UserService.get_user_by_id(user_id)
    if result['success']:
        return jsonify(result), 200
    return jsonify(result), 404


@user_bp.route('/api/users', methods=['POST'])
@admin_required
def create_user():
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided', 'success': False}), 400
    result = UserService.create_user(data)
    if result['success']:
        return jsonify(result), 201
    return jsonify(result), 400


@user_bp.route('/api/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided', 'success': False}), 400
    result = UserService.update_user(user_id, data)
    if result['success']:
        return jsonify(result), 200
    return jsonify(result), 400


@user_bp.route('/api/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    result = UserService.delete_user(user_id)
    if result['success']:
        return jsonify(result), 200
    return jsonify(result), 400


@user_bp.route('/api/users/<int:user_id>/status', methods=['PUT'])
@admin_required
def toggle_user_status(user_id):
    data = request.get_json()
    result = UserService.toggle_user_status(user_id, data.get('status'))
    if result['success']:
        return jsonify(result), 200
    return jsonify(result), 400


@user_bp.route('/api/roles', methods=['GET'])
@token_required
def get_roles():
    result = UserService.get_all_roles()
    return jsonify(result), 200 if result['success'] else 500


@user_bp.route('/api/managers', methods=['GET'])
@token_required
def get_managers():
    result = UserService.get_managers()
    return jsonify(result), 200 if result['success'] else 500


@user_bp.route('/api/employees', methods=['GET'])
@token_required
def get_employees():
    result = UserService.get_employees()
    return jsonify(result), 200 if result['success'] else 500


@user_bp.route('/api/dashboard-stats', methods=['GET'])
@token_required
def get_dashboard_stats():
    result = UserService.get_dashboard_stats(g.current_user_id, g.current_role_name)
    return jsonify(result), 200 if result['success'] else 500
