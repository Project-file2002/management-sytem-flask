from database.connection import DatabaseConnection


class NotificationService:

    @staticmethod
    def get_notifications(user_id):
        db = DatabaseConnection()
        try:
            query = """
                SELECT * FROM Notifications 
                WHERE user_id = ? 
                ORDER BY created_at DESC
            """
            notifications = db.execute_query(query, (user_id,))
            return {'success': True, 'data': notifications}
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}

    @staticmethod
    def get_unread_count(user_id):
        db = DatabaseConnection()
        try:
            result = db.execute_query(
                "SELECT COUNT(*) as count FROM Notifications WHERE user_id = ? AND is_read = 0",
                (user_id,)
            )
            return result[0]['count'] if result else 0
        except Exception as e:
            return 0

    @staticmethod
    def create_notification(user_id, title, message, notification_type):
        db = DatabaseConnection()
        try:
            db.execute_query(
                "INSERT INTO Notifications (user_id, title, message, type) VALUES (?, ?, ?, ?)",
                (user_id, title, message, notification_type),
                commit=True
            )
            return True
        except Exception as e:
            print(f"Notification error: {e}")
            return False

    @staticmethod
    def mark_as_read(notification_id, user_id):
        db = DatabaseConnection()
        try:
            db.execute_query(
                "UPDATE Notifications SET is_read = 1 WHERE notification_id = ? AND user_id = ?",
                (notification_id, user_id),
                commit=True
            )
            return {'success': True, 'message': 'Notification marked as read'}
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}

    @staticmethod
    def mark_all_as_read(user_id):
        db = DatabaseConnection()
        try:
            db.execute_query(
                "UPDATE Notifications SET is_read = 1 WHERE user_id = ?",
                (user_id,),
                commit=True
            )
            return {'success': True, 'message': 'All notifications marked as read'}
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}
