from flask import Blueprint, request, jsonify, g
from services.project_service import ProjectService
from middleware.auth_middleware import admin_required, token_required, manager_or_admin_required

project_bp = Blueprint('projects', __name__)


@project_bp.route('/api/projects', methods=['GET'])
@token_required
def get_projects():
    result = ProjectService.get_all_projects(g.current_user_id, g.current_role_name)
    return jsonify(result), 200 if result['success'] else 500


@project_bp.route('/api/projects/<int:project_id>', methods=['GET'])
@token_required
def get_project(project_id):
    result = ProjectService.get_project_by_id(project_id)
    if result['success']:
        return jsonify(result), 200
    return jsonify(result), 404


@project_bp.route('/api/projects', methods=['POST'])
@admin_required
def create_project():
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided', 'success': False}), 400
    result = ProjectService.create_project(data)
    if result['success']:
        return jsonify(result), 201
    return jsonify(result), 400


@project_bp.route('/api/projects/<int:project_id>', methods=['PUT'])
@admin_required
def update_project(project_id):
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided', 'success': False}), 400
    result = ProjectService.update_project(project_id, data)
    if result['success']:
        return jsonify(result), 200
    return jsonify(result), 400


@project_bp.route('/api/projects/<int:project_id>', methods=['DELETE'])
@admin_required
def delete_project(project_id):
    result = ProjectService.delete_project(project_id)
    if result['success']:
        return jsonify(result), 200
    return jsonify(result), 400
