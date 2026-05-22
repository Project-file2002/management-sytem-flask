import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'task-expense-mgmt-secret-key-2024')
    DEBUG = os.environ.get('DEBUG', True)

    # Sensible defaults for local development on Windows — updated to your local MSSQL server
    DB_SERVER = os.environ.get('DB_SERVER', 'ABHISHEK')
    DB_DATABASE = os.environ.get('DB_DATABASE', 'TaskExpenseDB')
    DB_USERNAME = os.environ.get('DB_USERNAME', 'sa')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    # Use ODBC Driver 18 if available; fall back to env override
    DB_DRIVER = os.environ.get('DB_DRIVER', '{ODBC Driver 18 for SQL Server}')
    # Set to 'yes' to use Windows trusted connection by default for local SQL Express
    DB_TRUSTED = os.environ.get('DB_TRUSTED', 'yes')

    # Allow overriding the full connection string via env var (preferred when using complex options)
    DB_CONNECTION_STRING = os.environ.get('DB_CONNECTION_STRING')

    if not DB_CONNECTION_STRING:
        # optional connection flags with sensible defaults for Windows Integrated Auth
        DB_ENCRYPT = os.environ.get('DB_ENCRYPT', 'True')
        DB_TRUST_SERVER_CERT = os.environ.get('DB_TRUST_SERVER_CERT', 'True')
        DB_APP_NAME = os.environ.get('DB_APP_NAME', 'vscode-mssql')
        DB_CONNECT_TIMEOUT = os.environ.get('DB_CONNECT_TIMEOUT', '30')
        DB_POOLING = os.environ.get('DB_POOLING', 'False')

        # normalize boolean-like values to 'yes'/'no' which ODBC expects
        def _to_yes_no(val):
            return 'yes' if str(val).lower() in ('1', 'true', 'yes', 'y', 'on') else 'no'

        DB_ENCRYPT = _to_yes_no(DB_ENCRYPT)
        DB_TRUST_SERVER_CERT = _to_yes_no(DB_TRUST_SERVER_CERT)
        DB_POOLING = _to_yes_no(DB_POOLING)

        if str(DB_TRUSTED).lower() in ('yes', 'true', '1'):
            DB_CONNECTION_STRING = (
                f"DRIVER={DB_DRIVER};"
                f"SERVER={DB_SERVER};"
                f"DATABASE={DB_DATABASE};"
                f"Trusted_Connection=yes;"
                f"Encrypt={DB_ENCRYPT};"
                f"TrustServerCertificate={DB_TRUST_SERVER_CERT};"
                f"Application Name={DB_APP_NAME};"
                f"Connect Timeout={DB_CONNECT_TIMEOUT};"
                f"Pooling={DB_POOLING}"
            )
        else:
            DB_CONNECTION_STRING = (
                f"DRIVER={DB_DRIVER};"
                f"SERVER={DB_SERVER};"
                f"DATABASE={DB_DATABASE};"
                f"UID={DB_USERNAME};"
                f"PWD={DB_PASSWORD};"
                f"Encrypt={DB_ENCRYPT};"
                f"TrustServerCertificate={DB_TRUST_SERVER_CERT};"
                f"Connect Timeout={DB_CONNECT_TIMEOUT};"
                f"Pooling={DB_POOLING}"
            )

    UPLOAD_FOLDER = os.environ.get(
        'UPLOAD_FOLDER',
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads')
    )
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
