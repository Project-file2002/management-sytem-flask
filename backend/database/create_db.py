import os
import sys
import pathlib
import pyodbc

# Ensure backend package directory is on sys.path so `from config.config import Config` works
backend_dir = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_dir))

from config.config import Config


def build_master_connection_string():
    # prefer explicit env override
    conn = os.environ.get('DB_CONNECTION_STRING')
    if conn:
        # replace database with master if present
        return conn.replace(f"DATABASE={Config.DB_DATABASE}", "DATABASE=master")

    driver = Config.DB_DRIVER
    server = Config.DB_SERVER
    timeout = os.environ.get('DB_CONNECT_TIMEOUT', '30')
    encrypt = os.environ.get('DB_ENCRYPT', 'True')
    trust_cert = os.environ.get('DB_TRUST_SERVER_CERT', 'True')

    # normalize boolean-like values
    def _to_yes_no(val):
        return 'yes' if str(val).lower() in ('1', 'true', 'yes', 'y', 'on') else 'no'

    encrypt = _to_yes_no(encrypt)
    trust_cert = _to_yes_no(trust_cert)

    if str(Config.DB_TRUSTED).lower() in ('yes', 'true', '1'):
        return (
            f"DRIVER={driver};"
            f"SERVER={server};"
            f"DATABASE=master;"
            f"Trusted_Connection=yes;"
            f"Encrypt={encrypt};"
            f"TrustServerCertificate={trust_cert};"
            f"Connect Timeout={timeout};"
            f"Pooling=no"
        )
    else:
        return (
            f"DRIVER={driver};"
            f"SERVER={server};"
            f"DATABASE=master;"
            f"UID={Config.DB_USERNAME};"
            f"PWD={Config.DB_PASSWORD};"
            f"Encrypt={encrypt};"
            f"TrustServerCertificate={trust_cert};"
            f"Connect Timeout={timeout};"
            f"Pooling=no"
        )


def main():
    conn_str = build_master_connection_string()
    print("Connecting to SQL Server using:")
    print(conn_str)

    try:
        conn = pyodbc.connect(conn_str)
        conn.autocommit = True
        cursor = conn.cursor()

        # get current login name (SUSER_SNAME) which returns domain\\user for Windows auth
        cursor.execute("SELECT SUSER_SNAME()")
        login = cursor.fetchone()[0]
        print(f"Current login: {login}")

        # create database if not exists
        cursor.execute("SELECT DB_ID('TaskExpenseDB')")
        exists = cursor.fetchone()[0]
        if not exists:
            print("Creating database TaskExpenseDB...")
            cursor.execute("CREATE DATABASE TaskExpenseDB")
            print("Database created")
        else:
            print("Database TaskExpenseDB already exists")

        # ensure login exists at server level (only for Windows logins)
        if login and '\\' in login:
            cursor.execute("SELECT COUNT(*) FROM sys.server_principals WHERE name = ?", (login,))
            if cursor.fetchone()[0] == 0:
                print(f"Creating server login {login}...")
                cursor.execute(f"CREATE LOGIN [{login}] FROM WINDOWS")
                print("Server login created")
            else:
                print("Server login already exists")

            # create user in the DB and add to db_owner
            cursor.execute("USE TaskExpenseDB")
            cursor.execute("SELECT COUNT(*) FROM sys.database_principals WHERE name = ?", (login,))
            if cursor.fetchone()[0] == 0:
                print(f"Creating database user {login}...")
                try:
                    cursor.execute(f"CREATE USER [{login}] FOR LOGIN [{login}]")
                    print("Database user created")
                except Exception as e:
                    msg = str(e)
                    if '15063' in msg or "login already has an account with the user name 'dbo'" in msg:
                        print("User mapping already exists as dbo; continuing")
                    else:
                        raise
            else:
                print("Database user already exists")

            print(f"Adding {login} to db_owner role...")
            try:
                cursor.execute(f"ALTER ROLE db_owner ADD MEMBER [{login}]")
            except Exception:
                try:
                    cursor.execute("EXEC sp_addrolemember 'db_owner', ?", (login,))
                except Exception:
                    print("Could not add to db_owner or already a member; continuing")
            print("Added to db_owner (or was already a member)")
        else:
            print("Login name not detected as Windows login; skipping Windows-login user creation")

        print("All done. Verify by running your Flask app to initialize tables.")

    except Exception as e:
        print(f"Error while creating database or users: {e}")
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass


if __name__ == '__main__':
    main()
