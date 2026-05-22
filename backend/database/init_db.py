from werkzeug.security import generate_password_hash
from database.connection import DatabaseConnection


def initialize_database():
    db = DatabaseConnection()
    conn = db.get_connection()
    cursor = conn.cursor()

    queries = [
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Roles')
        CREATE TABLE Roles (
            role_id INT IDENTITY(1,1) PRIMARY KEY,
            role_name NVARCHAR(50) NOT NULL UNIQUE,
            description NVARCHAR(255),
            created_at DATETIME DEFAULT GETDATE()
        )
        """,
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Users')
        CREATE TABLE Users (
            user_id INT IDENTITY(1,1) PRIMARY KEY,
            full_name NVARCHAR(100) NOT NULL,
            email NVARCHAR(100) NOT NULL UNIQUE,
            phone NVARCHAR(20),
            password_hash NVARCHAR(255) NOT NULL,
            department NVARCHAR(100),
            role_id INT NOT NULL,
            status NVARCHAR(20) DEFAULT 'Active',
            created_at DATETIME DEFAULT GETDATE(),
            updated_at DATETIME DEFAULT GETDATE(),
            FOREIGN KEY (role_id) REFERENCES Roles(role_id)
        )
        """,
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Projects')
        CREATE TABLE Projects (
            project_id INT IDENTITY(1,1) PRIMARY KEY,
            project_name NVARCHAR(200) NOT NULL,
            description NVARCHAR(MAX),
            start_date DATE,
            end_date DATE,
            manager_id INT,
            status NVARCHAR(20) DEFAULT 'Planned',
            created_at DATETIME DEFAULT GETDATE(),
            updated_at DATETIME DEFAULT GETDATE(),
            FOREIGN KEY (manager_id) REFERENCES Users(user_id)
        )
        """,
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Tasks')
        CREATE TABLE Tasks (
            task_id INT IDENTITY(1,1) PRIMARY KEY,
            task_title NVARCHAR(200) NOT NULL,
            task_description NVARCHAR(MAX),
            project_id INT,
            assigned_to INT,
            priority NVARCHAR(20) DEFAULT 'Medium',
            deadline DATE,
            status NVARCHAR(20) DEFAULT 'Pending',
            created_at DATETIME DEFAULT GETDATE(),
            updated_at DATETIME DEFAULT GETDATE(),
            FOREIGN KEY (project_id) REFERENCES Projects(project_id),
            FOREIGN KEY (assigned_to) REFERENCES Users(user_id)
        )
        """,
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Expenses')
        CREATE TABLE Expenses (
            expense_id INT IDENTITY(1,1) PRIMARY KEY,
            employee_id INT NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            category NVARCHAR(50) NOT NULL,
            description NVARCHAR(MAX),
            bill_path NVARCHAR(255),
            submitted_date DATETIME DEFAULT GETDATE(),
            approval_status NVARCHAR(20) DEFAULT 'Pending',
            approved_by INT,
            approved_date DATETIME,
            rejection_reason NVARCHAR(MAX),
            FOREIGN KEY (employee_id) REFERENCES Users(user_id),
            FOREIGN KEY (approved_by) REFERENCES Users(user_id)
        )
        """,
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Notifications')
        CREATE TABLE Notifications (
            notification_id INT IDENTITY(1,1) PRIMARY KEY,
            user_id INT NOT NULL,
            title NVARCHAR(200) NOT NULL,
            message NVARCHAR(MAX),
            type NVARCHAR(50),
            is_read BIT DEFAULT 0,
            created_at DATETIME DEFAULT GETDATE(),
            FOREIGN KEY (user_id) REFERENCES Users(user_id)
        )
        """,
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ProjectTeam')
        CREATE TABLE ProjectTeam (
            id INT IDENTITY(1,1) PRIMARY KEY,
            project_id INT NOT NULL,
            user_id INT NOT NULL,
            FOREIGN KEY (project_id) REFERENCES Projects(project_id),
            FOREIGN KEY (user_id) REFERENCES Users(user_id)
        )
        """,
        """
        IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Users_Email')
        CREATE INDEX IX_Users_Email ON Users(email)
        """,
        """
        IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Tasks_AssignedTo')
        CREATE INDEX IX_Tasks_AssignedTo ON Tasks(assigned_to)
        """,
        """
        IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Tasks_ProjectId')
        CREATE INDEX IX_Tasks_ProjectId ON Tasks(project_id)
        """,
        """
        IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Tasks_Status')
        CREATE INDEX IX_Tasks_Status ON Tasks(status)
        """,
        """
        IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Expenses_EmployeeId')
        CREATE INDEX IX_Expenses_EmployeeId ON Expenses(employee_id)
        """,
        """
        IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Expenses_ApprovalStatus')
        CREATE INDEX IX_Expenses_ApprovalStatus ON Expenses(approval_status)
        """,
        """
        IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Notifications_UserId')
        CREATE INDEX IX_Notifications_UserId ON Notifications(user_id)
        """,
        """
        IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Projects_ManagerId')
        CREATE INDEX IX_Projects_ManagerId ON Projects(manager_id)
        """
    ]

    try:
        for query in queries:
            cursor.execute(query)
        conn.commit()
        print("Database tables initialized successfully")

        seed_data(cursor, conn)

    except Exception as e:
        conn.rollback()
        print(f"Database initialization error: {e}")
        raise
    finally:
        cursor.close()


def seed_data(cursor, conn):
    cursor.execute("SELECT COUNT(*) FROM Roles")
    if cursor.fetchone()[0] == 0:
        roles = [
            ("Admin", "System administrator with full access"),
            ("Manager", "Project manager with team oversight"),
            ("Employee", "Team member with task and expense access")
        ]
        for role_name, description in roles:
            cursor.execute(
                "INSERT INTO Roles (role_name, description) VALUES (?, ?)",
                (role_name, description)
            )

        admin_password = generate_password_hash("Admin@123")
        cursor.execute(
            "INSERT INTO Users (full_name, email, phone, password_hash, department, role_id, status) VALUES (?, ?, ?, ?, ?, (SELECT role_id FROM Roles WHERE role_name='Admin'), 'Active')",
            ("System Admin", "admin@system.com", "1234567890", admin_password, "Administration")
        )

        conn.commit()
        print("Default roles and admin user created")
