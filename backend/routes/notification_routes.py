from flask import Blueprint, request, jsonify, g
from services.notification_service import NotificationService
from middleware.auth_middleware import token_required

notification_bp = Blueprint('notifications', __name__)


@notification_bp.route('/api/notifications', methods=['GET'])
@token_required
def get_notifications():
    result = NotificationService.get_notifications(g.current_user_id)
    return jsonify(result), 200 if result['success'] else 500


@notification_bp.route('/api/notifications/unread-count', methods=['GET'])
@token_required
def get_unread_count():
    count = NotificationService.get_unread_count(g.current_user_id)
    return jsonify({'success': True, 'count': count}), 200


@notification_bp.route('/api/notifications/<int:notification_id>/read', methods=['PUT'])
@token_required
def mark_as_read(notification_id):
    result = NotificationService.mark_as_read(notification_id, g.current_user_id)
    if result['success']:
        return jsonify(result), 200
    return jsonify(result), 400


@notification_bp.route('/api/notifications/read-all', methods=['PUT'])
@token_required
def mark_all_as_read():
    result = NotificationService.mark_all_as_read(g.current_user_id)
    if result['success']:
        return jsonify(result), 200
    return jsonify(result), 400
