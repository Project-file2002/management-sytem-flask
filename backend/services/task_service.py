from database.connection import DatabaseConnection
from services.notification_service import NotificationService


class TaskService:

    @staticmethod
    def get_all_tasks(user_id, role_name, project_id=None):
        db = DatabaseConnection()
        try:
            if role_name == 'Admin':
                if project_id:
                    query = """
                        SELECT t.*, u.full_name as assigned_to_name, p.project_name 
                        FROM Tasks t
                        LEFT JOIN Users u ON t.assigned_to = u.user_id
                        LEFT JOIN Projects p ON t.project_id = p.project_id
                        WHERE t.project_id = ?
                        ORDER BY t.created_at DESC
                    """
                    tasks = db.execute_query(query, (project_id,))
                else:
                    query = """
                        SELECT t.*, u.full_name as assigned_to_name, p.project_name 
                        FROM Tasks t
                        LEFT JOIN Users u ON t.assigned_to = u.user_id
                        LEFT JOIN Projects p ON t.project_id = p.project_id
                        ORDER BY t.created_at DESC
                    """
                    tasks = db.execute_query(query)

            elif role_name == 'Manager':
                if project_id:
                    query = """
                        SELECT t.*, u.full_name as assigned_to_name, p.project_name 
                        FROM Tasks t
                        LEFT JOIN Users u ON t.assigned_to = u.user_id
                        LEFT JOIN Projects p ON t.project_id = p.project_id
                        WHERE t.project_id = ? AND p.manager_id = ?
                        ORDER BY t.created_at DESC
                    """
                    tasks = db.execute_query(query, (project_id, user_id))
                else:
                    query = """
                        SELECT t.*, u.full_name as assigned_to_name, p.project_name 
                        FROM Tasks t
                        LEFT JOIN Users u ON t.assigned_to = u.user_id
                        LEFT JOIN Projects p ON t.project_id = p.project_id
                        WHERE p.manager_id = ?
                        ORDER BY t.created_at DESC
                    """
                    tasks = db.execute_query(query, (user_id,))

            else:
                if project_id:
                    query = """
                        SELECT t.*, u.full_name as assigned_to_name, p.project_name 
                        FROM Tasks t
                        LEFT JOIN Users u ON t.assigned_to = u.user_id
                        LEFT JOIN Projects p ON t.project_id = p.project_id
                        WHERE t.assigned_to = ? AND t.project_id = ?
                        ORDER BY t.created_at DESC
                    """
                    tasks = db.execute_query(query, (user_id, project_id))
                else:
                    query = """
                        SELECT t.*, u.full_name as assigned_to_name, p.project_name 
                        FROM Tasks t
                        LEFT JOIN Users u ON t.assigned_to = u.user_id
                        LEFT JOIN Projects p ON t.project_id = p.project_id
                        WHERE t.assigned_to = ?
                        ORDER BY t.created_at DESC
                    """
                    tasks = db.execute_query(query, (user_id,))

            return {'success': True, 'data': tasks}
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}

    @staticmethod
    def get_task_by_id(task_id):
        db = DatabaseConnection()
        try:
            query = """
                SELECT t.*, u.full_name as assigned_to_name, p.project_name 
                FROM Tasks t
                LEFT JOIN Users u ON t.assigned_to = u.user_id
                LEFT JOIN Projects p ON t.project_id = p.project_id
                WHERE t.task_id = ?
            """
            result = db.execute_query(query, (task_id,))
            if not result:
                return {'success': False, 'message': 'Task not found'}
            return {'success': True, 'data': result[0]}
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}

    @staticmethod
    def create_task(data, created_by):
        db = DatabaseConnection()
        try:
            task_title = data.get('task_title', '').strip()
            task_description = data.get('task_description', '').strip()
            project_id = data.get('project_id')
            assigned_to = data.get('assigned_to')
            priority = data.get('priority', 'Medium')
            deadline = data.get('deadline')

            if not task_title:
                return {'success': False, 'message': 'Task title is required'}

            insert_query = """
                INSERT INTO Tasks (task_title, task_description, project_id, assigned_to, priority, deadline)
                OUTPUT INSERTED.task_id
                VALUES (?, ?, ?, ?, ?, ?)
            """
            new_id = db.execute_query(
                insert_query,
                (task_title, task_description, project_id, assigned_to, priority, deadline),
                commit=True
            )

            if assigned_to:
                NotificationService.create_notification(
                    assigned_to,
                    'Task Assigned',
                    f'New task "{task_title}" has been assigned to you.',
                    'task_assigned'
                )

            return {
                'success': True,
                'message': 'Task created successfully',
                'task_id': new_id[0]['task_id'] if new_id else None
            }
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}

    @staticmethod
    def update_task(task_id, data, user_id, role_name):
        db = DatabaseConnection()
        try:
            task_title = data.get('task_title', '').strip()
            task_description = data.get('task_description', '').strip()
            project_id = data.get('project_id')
            assigned_to = data.get('assigned_to')
            priority = data.get('priority')
            deadline = data.get('deadline')
            status = data.get('status')

            current_task = TaskService.get_task_by_id(task_id)
            if not current_task['success']:
                return current_task

            update_query = """
                UPDATE Tasks 
                SET task_title = ?, task_description = ?, project_id = ?, 
                    assigned_to = ?, priority = ?, deadline = ?, status = ?, updated_at = GETDATE()
                WHERE task_id = ?
            """
            db.execute_query(
                update_query,
                (task_title, task_description, project_id, assigned_to, priority, deadline, status, task_id),
                commit=True
            )

            if assigned_to:
                NotificationService.create_notification(
                    assigned_to,
                    'Task Updated',
                    f'Task "{task_title}" has been updated.',
                    'task_updated'
                )

            return {'success': True, 'message': 'Task updated successfully'}
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}

    @staticmethod
    def delete_task(task_id):
        db = DatabaseConnection()
        try:
            db.execute_query("DELETE FROM Tasks WHERE task_id = ?", (task_id,), commit=True)
            return {'success': True, 'message': 'Task deleted successfully'}
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}

    @staticmethod
    def update_task_status(task_id, status, user_id):
        db = DatabaseConnection()
        try:
            valid_statuses = ['Pending', 'In Progress', 'Awaiting Approval', 'Completed']
            if status not in valid_statuses:
                return {'success': False, 'message': 'Invalid status'}

            query = """
                SELECT t.*, p.manager_id, p.project_name,
                       (SELECT full_name FROM Users WHERE user_id = t.assigned_to) as assigned_name
                FROM Tasks t
                LEFT JOIN Projects p ON t.project_id = p.project_id
                WHERE t.task_id = ?
            """
            task = db.execute_query(query, (task_id,))

            if not task:
                return {'success': False, 'message': 'Task not found'}

            task = task[0]

            role_query = """
                SELECT r.role_name FROM Users u
                JOIN Roles r ON u.role_id = r.role_id
                WHERE u.user_id = ?
            """
            role_result = db.execute_query(role_query, (user_id,))
            role_name = role_result[0]['role_name'] if role_result else 'Employee'

            if role_name == 'Employee' and task.get('assigned_to') != user_id:
                return {'success': False, 'message': 'You can only update your own tasks'}

            db.execute_query(
                "UPDATE Tasks SET status = ?, updated_at = GETDATE() WHERE task_id = ?",
                (status, task_id),
                commit=True
            )

            if status == 'Awaiting Approval' and task.get('manager_id'):
                NotificationService.create_notification(
                    task['manager_id'],
                    'Task Pending Approval',
                    f'Task "{task["task_title"]}" in project "{task["project_name"]}" is awaiting your approval.',
                    'task_pending_approval'
                )
            elif status == 'Completed' and task.get('assigned_to') and task['assigned_to'] != user_id:
                NotificationService.create_notification(
                    task['assigned_to'],
                    'Task Approved',
                    f'Your task "{task["task_title"]}" has been approved.',
                    'task_approved'
                )
            elif status == 'In Progress' and task.get('assigned_to'):
                prev_status = task.get('status', '')
                if prev_status == 'Awaiting Approval':
                    NotificationService.create_notification(
                        task['assigned_to'],
                        'Task Changes Requested',
                        f'Your task "{task["task_title"]}" needs changes. Please review.',
                        'task_changes_requested'
                    )
            elif task.get('manager_id') and task['manager_id'] != user_id:
                NotificationService.create_notification(
                    task['manager_id'],
                    'Task Status Updated',
                    f'Task "{task["task_title"]}" in project "{task["project_name"]}" changed to {status}.',
                    'task_updated'
                )

            return {'success': True, 'message': f'Task status updated to {status}'}
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}
