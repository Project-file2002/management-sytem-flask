from flask import Blueprint, request, jsonify, g
from services.task_service import TaskService
from middleware.auth_middleware import token_required, manager_or_admin_required

task_bp = Blueprint('tasks', __name__)


@task_bp.route('/api/tasks', methods=['GET'])
@token_required
def get_tasks():
    project_id = request.args.get('project_id', type=int)
    result = TaskService.get_all_tasks(g.current_user_id, g.current_role_name, project_id)
    return jsonify(result), 200 if result['success'] else 500


@task_bp.route('/api/tasks/<int:task_id>', methods=['GET'])
@token_required
def get_task(task_id):
    result = TaskService.get_task_by_id(task_id)
    if result['success']:
        return jsonify(result), 200
    return jsonify(result), 404


@task_bp.route('/api/tasks', methods=['POST'])
@manager_or_admin_required
def create_task():
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided', 'success': False}), 400
    result = TaskService.create_task(data, g.current_user_id)
    if result['success']:
        return jsonify(result), 201
    return jsonify(result), 400


@task_bp.route('/api/tasks/<int:task_id>', methods=['PUT'])
@token_required
def update_task(task_id):
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided', 'success': False}), 400
    result = TaskService.update_task(task_id, data, g.current_user_id, g.current_role_name)
    if result['success']:
        return jsonify(result), 200
    return jsonify(result), 400


@task_bp.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@manager_or_admin_required
def delete_task(task_id):
    result = TaskService.delete_task(task_id)
    if result['success']:
        return jsonify(result), 200
    return jsonify(result), 400


@task_bp.route('/api/tasks/<int:task_id>/status', methods=['PUT'])
@token_required
def update_task_status(task_id):
    data = request.get_json()
    result = TaskService.update_task_status(task_id, data.get('status'), g.current_user_id)
    if result['success']:
        return jsonify(result), 200
    return jsonify(result), 400
