from database.connection import DatabaseConnection
from services.notification_service import NotificationService


class ProjectService:

    @staticmethod
    def get_all_projects(user_id, role_name):
        db = DatabaseConnection()
        try:
            if role_name == 'Admin':
                query = """
                    SELECT p.*, u.full_name as manager_name 
                    FROM Projects p
                    LEFT JOIN Users u ON p.manager_id = u.user_id
                    ORDER BY p.created_at DESC
                """
                projects = db.execute_query(query)
            elif role_name == 'Manager':
                query = """
                    SELECT p.*, u.full_name as manager_name 
                    FROM Projects p
                    LEFT JOIN Users u ON p.manager_id = u.user_id
                    WHERE p.manager_id = ?
                    ORDER BY p.created_at DESC
                """
                projects = db.execute_query(query, (user_id,))
            else:
                query = """
                    SELECT DISTINCT p.*, u.full_name as manager_name 
                    FROM Projects p
                    LEFT JOIN Users u ON p.manager_id = u.user_id
                    LEFT JOIN Tasks t ON p.project_id = t.project_id
                    WHERE t.assigned_to = ? OR p.manager_id = ?
                    ORDER BY p.created_at DESC
                """
                projects = db.execute_query(query, (user_id, user_id))

            return {'success': True, 'data': projects}
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}

    @staticmethod
    def get_project_by_id(project_id):
        db = DatabaseConnection()
        try:
            query = """
                SELECT p.*, u.full_name as manager_name 
                FROM Projects p
                LEFT JOIN Users u ON p.manager_id = u.user_id
                WHERE p.project_id = ?
            """
            result = db.execute_query(query, (project_id,))
            if not result:
                return {'success': False, 'message': 'Project not found'}
            return {'success': True, 'data': result[0]}
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}

    @staticmethod
    def create_project(data):
        db = DatabaseConnection()
        try:
            project_name = data.get('project_name', '').strip()
            description = data.get('description', '').strip()
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            manager_id = data.get('manager_id')
            status = data.get('status', 'Planned')

            if not project_name:
                return {'success': False, 'message': 'Project name is required'}

            insert_query = """
                INSERT INTO Projects (project_name, description, start_date, end_date, manager_id, status)
                OUTPUT INSERTED.project_id
                VALUES (?, ?, ?, ?, ?, ?)
            """
            new_id = db.execute_query(
                insert_query,
                (project_name, description, start_date, end_date, manager_id, status),
                commit=True
            )

            if manager_id:
                NotificationService.create_notification(
                    manager_id,
                    'Project Assigned',
                    f'You have been assigned as manager for project "{project_name}".',
                    'project_assigned'
                )

            return {
                'success': True,
                'message': 'Project created successfully',
                'project_id': new_id[0]['project_id'] if new_id else None
            }
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}

    @staticmethod
    def update_project(project_id, data):
        db = DatabaseConnection()
        try:
            project_name = data.get('project_name', '').strip()
            description = data.get('description', '').strip()
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            manager_id = data.get('manager_id')
            status = data.get('status')

            if not project_name:
                return {'success': False, 'message': 'Project name is required'}

            current = ProjectService.get_project_by_id(project_id)
            old_manager_id = current['data']['manager_id'] if current['success'] else None

            update_query = """
                UPDATE Projects 
                SET project_name = ?, description = ?, start_date = ?, end_date = ?, 
                    manager_id = ?, status = ?, updated_at = GETDATE()
                WHERE project_id = ?
            """
            db.execute_query(
                update_query,
                (project_name, description, start_date, end_date, manager_id, status, project_id),
                commit=True
            )

            if manager_id and manager_id != old_manager_id:
                NotificationService.create_notification(
                    manager_id,
                    'Project Assigned',
                    f'You have been assigned as manager for project "{project_name}".',
                    'project_assigned'
                )

            return {'success': True, 'message': 'Project updated successfully'}
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}

    @staticmethod
    def delete_project(project_id):
        db = DatabaseConnection()
        try:
            db.execute_query("DELETE FROM Tasks WHERE project_id = ?", (project_id,), commit=True)
            db.execute_query("DELETE FROM Projects WHERE project_id = ?", (project_id,), commit=True)
            return {'success': True, 'message': 'Project deleted successfully'}
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}
