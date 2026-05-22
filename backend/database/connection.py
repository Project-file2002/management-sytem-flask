import pyodbc
import time
from config.config import Config


class DatabaseConnection:

    def __init__(self):
        self.connection = None

    def connect(self):
        if self.connection is not None:
            try:
                self.connection.close()
            except pyodbc.Error:
                pass
            self.connection = None
        try:
            self.connection = pyodbc.connect(Config.DB_CONNECTION_STRING)
            self.connection.autocommit = False
        except pyodbc.Error as e:
            print(f"Database connection error: {e}")
            raise
        return self.connection

    def get_connection(self):
        if self.connection is not None:
            try:
                cursor = self.connection.cursor()
                cursor.execute("SELECT 1")
                cursor.close()
                return self.connection
            except pyodbc.Error:
                try:
                    self.connection.close()
                except pyodbc.Error:
                    pass
                self.connection = None
        return self.connect()

    def close(self):
        if self.connection:
            try:
                self.connection.close()
            except pyodbc.Error:
                pass
            self.connection = None

    def execute_query(self, query, params=None, commit=False):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            if cursor.description:
                columns = [column[0] for column in cursor.description]
                rows = cursor.fetchall()
                result = []
                for row in rows:
                    result.append(dict(zip(columns, row)))
            else:
                result = None
            if commit:
                conn.commit()
            return result
        except pyodbc.Error as e:
            if commit:
                try:
                    conn.rollback()
                except pyodbc.Error:
                    pass
            raise e
        finally:
            cursor.close()

    def execute_procedure(self, proc_name, params=None, commit=False):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            if params:
                cursor.execute(f"EXEC {proc_name} {', '.join(['?' for _ in params])}", params)
            else:
                cursor.execute(f"EXEC {proc_name}")
            if commit:
                conn.commit()
                return True
            columns = [column[0] for column in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            result = []
            for row in rows:
                result.append(dict(zip(columns, row)))
            return result
        except pyodbc.Error as e:
            if commit:
                try:
                    conn.rollback()
                except pyodbc.Error:
                    pass
            raise e
        finally:
            cursor.close()
