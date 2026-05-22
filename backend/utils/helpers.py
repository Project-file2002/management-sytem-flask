import os
from werkzeug.utils import secure_filename
from config.config import Config


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


def save_uploaded_file(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(upload_path)
        return filename
    return None


def format_date(date_obj):
    if date_obj:
        return date_obj.strftime('%Y-%m-%d')
    return None


def format_datetime(dt_obj):
    if dt_obj:
        return dt_obj.strftime('%Y-%m-%d %H:%M:%S')
    return None


def validate_email(email):
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def sanitize_input(input_str):
    if input_str:
        return input_str.strip()
    return input_str
