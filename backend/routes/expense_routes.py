from flask import Blueprint, request, jsonify, g
from services.expense_service import ExpenseService
from middleware.auth_middleware import token_required, manager_or_admin_required

expense_bp = Blueprint('expenses', __name__)


@expense_bp.route('/api/expenses', methods=['GET'])
@token_required
def get_expenses():
    result = ExpenseService.get_all_expenses(g.current_user_id, g.current_role_name)
    return jsonify(result), 200 if result['success'] else 500


@expense_bp.route('/api/expenses/<int:expense_id>', methods=['GET'])
@token_required
def get_expense(expense_id):
    result = ExpenseService.get_expense_by_id(expense_id)
    if result['success']:
        return jsonify(result), 200
    return jsonify(result), 404


@expense_bp.route('/api/expenses', methods=['POST'])
@token_required
def create_expense():
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided', 'success': False}), 400
    result = ExpenseService.create_expense(data, g.current_user_id)
    if result['success']:
        return jsonify(result), 201
    return jsonify(result), 400


@expense_bp.route('/api/expenses/upload-bill', methods=['POST'])
@token_required
def upload_bill():
    if 'bill' not in request.files:
        return jsonify({'message': 'No file provided', 'success': False}), 400
    file = request.files['bill']
    expense_id = request.form.get('expense_id', type=int)
    result = ExpenseService.upload_bill(expense_id, file)
    if result['success']:
        return jsonify(result), 200
    return jsonify(result), 400


@expense_bp.route('/api/expenses/<int:expense_id>/approve', methods=['PUT'])
@manager_or_admin_required
def approve_expense(expense_id):
    result = ExpenseService.approve_expense(expense_id, g.current_user_id)
    if result['success']:
        return jsonify(result), 200
    return jsonify(result), 400


@expense_bp.route('/api/expenses/<int:expense_id>/reject', methods=['PUT'])
@manager_or_admin_required
def reject_expense(expense_id):
    data = request.get_json()
    reason = data.get('reason', '') if data else ''
    result = ExpenseService.reject_expense(expense_id, g.current_user_id, reason)
    if result['success']:
        return jsonify(result), 200
    return jsonify(result), 400
