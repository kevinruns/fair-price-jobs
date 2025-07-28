import os
import uuid
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import current_app

class FileService:
    @staticmethod
    def allowed_file(filename):
        allowed = current_app.config.get('ALLOWED_EXTENSIONS', {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'txt'})
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed

    @staticmethod
    def save_file(file, folder='uploads'):
        if file and file.filename and FileService.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            upload_path = Path(current_app.config['UPLOAD_FOLDER']) / folder
            upload_path.mkdir(parents=True, exist_ok=True)
            file_path = upload_path / unique_filename
            file.save(str(file_path))
            return str(file_path.relative_to(current_app.config['UPLOAD_FOLDER']))
        return None

    @staticmethod
    def delete_file(filename):
        if not filename:
            return True
        try:
            file_path = Path(current_app.config['UPLOAD_FOLDER']) / filename
            if file_path.exists():
                file_path.unlink()
                return True
        except Exception:
            pass
        return False

    @staticmethod
    def get_file_url(filename):
        if not filename:
            return None
        return f"/uploads/{filename}" 