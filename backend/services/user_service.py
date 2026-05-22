from werkzeug.security import generate_password_hash
from database.connection import DatabaseConnection
from utils.helpers import validate_email


class UserService:

    @staticmethod
    def get_all_users():
        db = DatabaseConnection()
        try:
            query = """
                SELECT u.user_id, u.full_name, u.email, u.phone, 
                       u.department, r.role_name, u.role_id, u.status, u.created_at
                FROM Users u
                JOIN Roles r ON u.role_id = r.role_id
                ORDER BY u.created_at DESC
            """
            users = db.execute_query(query)
            return {'success': True, 'data': users}
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}

    @staticmethod
    def get_user_by_id(user_id):
        db = DatabaseConnection()
        try:
            query = """
                SELECT u.user_id, u.full_name, u.email, u.phone, 
                       u.department, r.role_name, u.role_id, u.status, u.created_at
                FROM Users u
                JOIN Roles r ON u.role_id = r.role_id
                WHERE u.user_id = ?
            """
            result = db.execute_query(query, (user_id,))
            if not result:
                return {'success': False, 'message': 'User not found'}
            return {'success': True, 'data': result[0]}
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}

    @staticmethod
    def create_user(data):
        db = DatabaseConnection()
        try:
            full_name = data.get('full_name', '').strip()
            email = data.get('email', '').strip().lower()
            phone = data.get('phone', '').strip()
            department = data.get('department', '').strip()
            role_id = data.get('role_id')
            password = data.get('password', 'Password@123')

            if not full_name or not email:
                return {'success': False, 'message': 'Name and email are required'}
            if not validate_email(email):
                return {'success': False, 'message': 'Invalid email format'}
            if not role_id:
                return {'success': False, 'message': 'Role is required'}

            check_query = "SELECT COUNT(*) as count FROM Users WHERE email = ?"
            existing = db.execute_query(check_query, (email,))
            if existing and existing[0]['count'] > 0:
                return {'success': False, 'message': 'Email already exists'}

            password_hash = generate_password_hash(password)
            insert_query = """
                INSERT INTO Users (full_name, email, phone, password_hash, department, role_id, status)
                OUTPUT INSERTED.user_id
                VALUES (?, ?, ?, ?, ?, ?, 'Active')
            """
            new_id = db.execute_query(
                insert_query,
                (full_name, email, phone, password_hash, department, role_id),
                commit=True
            )

            return {
                'success': True,
                'message': 'User created successfully',
                'user_id': new_id[0]['user_id'] if new_id else None
            }
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}

    @staticmethod
    def update_user(user_id, data):
        db = DatabaseConnection()
        try:
            full_name = data.get('full_name', '').strip()
            email = data.get('email', '').strip().lower()
            phone = data.get('phone', '').strip()
            department = data.get('department', '').strip()
            role_id = data.get('role_id')

            check_query = "SELECT COUNT(*) as count FROM Users WHERE email = ? AND user_id != ?"
            existing = db.execute_query(check_query, (email, user_id))
            if existing and existing[0]['count'] > 0:
                return {'success': False, 'message': 'Email already in use by another user'}

            update_query = """
                UPDATE Users 
                SET full_name = ?, email = ?, phone = ?, department = ?, role_id = ?, updated_at = GETDATE()
                WHERE user_id = ?
            """
            db.execute_query(update_query, (full_name, email, phone, department, role_id, user_id), commit=True)

            return {'success': True, 'message': 'User updated successfully'}
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}

    @staticmethod
    def delete_user(user_id):
        db = DatabaseConnection()
        try:
            check_query = "SELECT role_name FROM Users u JOIN Roles r ON u.role_id = r.role_id WHERE user_id = ?"
            user = db.execute_query(check_query, (user_id,))
            if user and user[0]['role_name'] == 'Admin':
                return {'success': False, 'message': 'Cannot delete admin user'}

            db.execute_query("DELETE FROM Users WHERE user_id = ?", (user_id,), commit=True)
            return {'success': True, 'message': 'User deleted successfully'}
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}

    @staticmethod
    def toggle_user_status(user_id, status):
        db = DatabaseConnection()
        try:
            if status not in ['Active', 'Inactive']:
                return {'success': False, 'message': 'Invalid status'}

            db.execute_query(
                "UPDATE Users SET status = ?, updated_at = GETDATE() WHERE user_id = ?",
                (status, user_id),
                commit=True
            )
            return {'success': True, 'message': f'User {status.lower()} successfully'}
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}

    @staticmethod
    def get_all_roles():
        db = DatabaseConnection()
        try:
            roles = db.execute_query("SELECT role_id, role_name, description FROM Roles")
            return {'success': True, 'data': roles}
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}

    @staticmethod
    def get_managers():
        db = DatabaseConnection()
        try:
            query = """
                SELECT user_id, full_name, email, department 
                FROM Users WHERE role_id = (SELECT role_id FROM Roles WHERE role_name='Manager') AND status = 'Active'
            """
            managers = db.execute_query(query)
            return {'success': True, 'data': managers}
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}

    @staticmethod
    def get_employees():
        db = DatabaseConnection()
        try:
            query = """
                SELECT user_id, full_name, email, department 
                FROM Users WHERE role_id = (SELECT role_id FROM Roles WHERE role_name='Employee') AND status = 'Active'
            """
            employees = db.execute_query(query)
            return {'success': True, 'data': employees}
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}

    @staticmethod
    def get_dashboard_stats(user_id, role_name):
        db = DatabaseConnection()
        try:
            stats = {}

            if role_name == 'Admin':
                stats['total_users'] = db.execute_query("SELECT COUNT(*) as count FROM Users")[0]['count']
                stats['total_projects'] = db.execute_query("SELECT COUNT(*) as count FROM Projects")[0]['count']
                stats['total_tasks'] = db.execute_query("SELECT COUNT(*) as count FROM Tasks")[0]['count']
                stats['total_expenses'] = db.execute_query("SELECT COUNT(*) as count FROM Expenses")[0]['count']
                stats['pending_tasks'] = db.execute_query("SELECT COUNT(*) as count FROM Tasks WHERE status = 'Pending'")[0]['count']
                stats['pending_expenses'] = db.execute_query("SELECT COUNT(*) as count FROM Expenses WHERE approval_status = 'Pending'")[0]['count']
                stats['active_projects'] = db.execute_query("SELECT COUNT(*) as count FROM Projects WHERE status = 'Active'")[0]['count']

            elif role_name == 'Manager':
                stats['total_projects'] = db.execute_query("SELECT COUNT(*) as count FROM Projects WHERE manager_id = ?", (user_id,))[0]['count']
                stats['total_tasks'] = db.execute_query(
                    "SELECT COUNT(*) as count FROM Tasks t JOIN Projects p ON t.project_id = p.project_id WHERE p.manager_id = ?",
                    (user_id,)
                )[0]['count']
                stats['pending_approvals'] = db.execute_query(
                    "SELECT COUNT(*) as count FROM Expenses WHERE approval_status = 'Pending' AND approved_by IS NULL"
                )[0]['count']
                stats['pending_tasks'] = db.execute_query(
                    "SELECT COUNT(*) as count FROM Tasks t JOIN Projects p ON t.project_id = p.project_id WHERE p.manager_id = ? AND t.status = 'Pending'",
                    (user_id,)
                )[0]['count']

            elif role_name == 'Employee':
                stats['assigned_tasks'] = db.execute_query("SELECT COUNT(*) as count FROM Tasks WHERE assigned_to = ?", (user_id,))[0]['count']
                stats['completed_tasks'] = db.execute_query("SELECT COUNT(*) as count FROM Tasks WHERE assigned_to = ? AND status = 'Completed'", (user_id,))[0]['count']
                stats['pending_tasks'] = db.execute_query("SELECT COUNT(*) as count FROM Tasks WHERE assigned_to = ? AND status = 'Pending'", (user_id,))[0]['count']
                stats['total_expenses'] = db.execute_query("SELECT COUNT(*) as count FROM Expenses WHERE employee_id = ?", (user_id,))[0]['count']
                stats['approved_expenses'] = db.execute_query("SELECT COUNT(*) as count FROM Expenses WHERE employee_id = ? AND approval_status = 'Approved'", (user_id,))[0]['count']

            return {'success': True, 'data': stats}
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}
