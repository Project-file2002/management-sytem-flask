from database.connection import DatabaseConnection
from services.notification_service import NotificationService
from utils.helpers import save_uploaded_file


class ExpenseService:

    @staticmethod
    def get_all_expenses(user_id, role_name):
        db = DatabaseConnection()
        try:
            if role_name == 'Admin':
                query = """
                    SELECT e.*, u.full_name as employee_name, ap.full_name as approved_by_name
                    FROM Expenses e
                    LEFT JOIN Users u ON e.employee_id = u.user_id
                    LEFT JOIN Users ap ON e.approved_by = ap.user_id
                    ORDER BY e.submitted_date DESC
                """
                expenses = db.execute_query(query)
            elif role_name == 'Manager':
                query = """
                    SELECT e.*, u.full_name as employee_name, ap.full_name as approved_by_name
                    FROM Expenses e
                    LEFT JOIN Users u ON e.employee_id = u.user_id
                    LEFT JOIN Users ap ON e.approved_by = ap.user_id
                    ORDER BY e.submitted_date DESC
                """
                expenses = db.execute_query(query)
            else:
                query = """
                    SELECT e.*, u.full_name as employee_name, ap.full_name as approved_by_name
                    FROM Expenses e
                    LEFT JOIN Users u ON e.employee_id = u.user_id
                    LEFT JOIN Users ap ON e.approved_by = ap.user_id
                    WHERE e.employee_id = ?
                    ORDER BY e.submitted_date DESC
                """
                expenses = db.execute_query(query, (user_id,))

            return {'success': True, 'data': expenses}
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}

    @staticmethod
    def get_expense_by_id(expense_id):
        db = DatabaseConnection()
        try:
            query = """
                SELECT e.*, u.full_name as employee_name, ap.full_name as approved_by_name
                FROM Expenses e
                LEFT JOIN Users u ON e.employee_id = u.user_id
                LEFT JOIN Users ap ON e.approved_by = ap.user_id
                WHERE e.expense_id = ?
            """
            result = db.execute_query(query, (expense_id,))
            if not result:
                return {'success': False, 'message': 'Expense not found'}
            return {'success': True, 'data': result[0]}
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}

    @staticmethod
    def create_expense(data, user_id):
        db = DatabaseConnection()
        try:
            amount = data.get('amount')
            category = data.get('category', '').strip()
            description = data.get('description', '').strip()

            if not amount or not category:
                return {'success': False, 'message': 'Amount and category are required'}

            insert_query = """
                INSERT INTO Expenses (employee_id, amount, category, description)
                OUTPUT INSERTED.expense_id
                VALUES (?, ?, ?, ?)
            """
            new_id = db.execute_query(
                insert_query,
                (user_id, amount, category, description),
                commit=True
            )

            return {
                'success': True,
                'message': 'Expense submitted successfully',
                'expense_id': new_id[0]['expense_id'] if new_id else None
            }
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}

    @staticmethod
    def upload_bill(expense_id, file):
        db = DatabaseConnection()
        try:
            if not expense_id:
                return {'success': False, 'message': 'Expense ID is required'}

            filename = save_uploaded_file(file)
            if not filename:
                return {'success': False, 'message': 'Invalid file type. Allowed: JPG, PNG, PDF'}

            db.execute_query(
                "UPDATE Expenses SET bill_path = ? WHERE expense_id = ?",
                (filename, expense_id),
                commit=True
            )

            return {'success': True, 'message': 'Bill uploaded successfully', 'filename': filename}
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}

    @staticmethod
    def approve_expense(expense_id, user_id):
        db = DatabaseConnection()
        try:
            expense = ExpenseService.get_expense_by_id(expense_id)
            if not expense['success']:
                return expense

            db.execute_query(
                "UPDATE Expenses SET approval_status = 'Approved', approved_by = ?, approved_date = GETDATE() WHERE expense_id = ?",
                (user_id, expense_id),
                commit=True
            )

            NotificationService.create_notification(
                expense['data']['employee_id'],
                'Expense Approved',
                f'Your expense of ${expense["data"]["amount"]} has been approved.',
                'expense_approved'
            )

            return {'success': True, 'message': 'Expense approved successfully'}
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}

    @staticmethod
    def reject_expense(expense_id, user_id, reason=''):
        db = DatabaseConnection()
        try:
            expense = ExpenseService.get_expense_by_id(expense_id)
            if not expense['success']:
                return expense

            db.execute_query(
                "UPDATE Expenses SET approval_status = 'Rejected', approved_by = ?, approved_date = GETDATE(), rejection_reason = ? WHERE expense_id = ?",
                (user_id, reason, expense_id),
                commit=True
            )

            NotificationService.create_notification(
                expense['data']['employee_id'],
                'Expense Rejected',
                f'Your expense of ${expense["data"]["amount"]} has been rejected. Reason: {reason}',
                'expense_rejected'
            )

            return {'success': True, 'message': 'Expense rejected successfully'}
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}
