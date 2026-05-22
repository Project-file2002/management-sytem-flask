from werkzeug.security import check_password_hash, generate_password_hash
from database.connection import DatabaseConnection
from middleware.auth_middleware import generate_token


class AuthService:

    @staticmethod
    def login(email, password):
        db = DatabaseConnection()
        try:
            query = """
                SELECT u.user_id, u.full_name, u.email, u.password_hash, 
                       u.role_id, r.role_name, u.status, u.department
                FROM Users u
                JOIN Roles r ON u.role_id = r.role_id
                WHERE u.email = ?
            """
            result = db.execute_query(query, (email,))

            if not result:
                return {'success': False, 'message': 'Invalid email or password'}

            user = result[0]

            if user['status'] != 'Active':
                return {'success': False, 'message': 'Account is deactivated. Contact admin.'}

            if not check_password_hash(user['password_hash'], password):
                return {'success': False, 'message': 'Invalid email or password'}

            token = generate_token(
                user['user_id'],
                user['role_id'],
                user['role_name']
            )

            return {
                'success': True,
                'message': 'Login successful',
                'token': token,
                'user': {
                    'user_id': user['user_id'],
                    'full_name': user['full_name'],
                    'email': user['email'],
                    'role': user['role_name'],
                    'department': user['department']
                }
            }
        except Exception as e:
            return {'success': False, 'message': f'Login error: {str(e)}'}

    @staticmethod
    def get_profile(user_id):
        db = DatabaseConnection()
        try:
            query = """
                SELECT u.user_id, u.full_name, u.email, u.phone, 
                       u.department, r.role_name, u.status, u.created_at
                FROM Users u
                JOIN Roles r ON u.role_id = r.role_id
                WHERE u.user_id = ?
            """
            result = db.execute_query(query, (user_id,))
            if not result:
                return {'success': False, 'message': 'User not found'}

            user = result[0]
            return {'success': True, 'data': user}
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}

    @staticmethod
    def change_password(user_id, current_password, new_password):
        db = DatabaseConnection()
        try:
            query = "SELECT password_hash FROM Users WHERE user_id = ?"
            result = db.execute_query(query, (user_id,))

            if not result:
                return {'success': False, 'message': 'User not found'}

            if not check_password_hash(result[0]['password_hash'], current_password):
                return {'success': False, 'message': 'Current password is incorrect'}

            new_hash = generate_password_hash(new_password)
            update_query = "UPDATE Users SET password_hash = ? WHERE user_id = ?"
            db.execute_query(update_query, (new_hash, user_id), commit=True)

            return {'success': True, 'message': 'Password changed successfully'}
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}
