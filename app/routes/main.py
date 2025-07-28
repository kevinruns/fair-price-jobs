from flask import Blueprint, render_template, request, flash, redirect, url_for, session, current_app, abort
from werkzeug.wrappers.response import Response
from typing import Any, Dict, List, Union, Optional
from app.helpers import login_required
from app.services.user_service import UserService
from app.services.group_service import GroupService
from app.services.tradesman_service import TradesmanService
from app.services.job_service import JobService
from app.services.file_service import FileService
from config import get_config
from pathlib import Path
import os

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
@login_required
def index() -> Union[str, Response]:
    """Show portfolio of tradesmen and recent jobs."""
    user_service = UserService()
    group_service = GroupService()
    tradesman_service = TradesmanService()
    job_service = JobService()
    
    user_id = session.get("user_id")
    if user_id is None:
        flash("User not logged in.", "error")
        return redirect(url_for("auth.login"))
    
    # Get user's tradesmen
    user_tradesmen = tradesman_service.get_tradesmen_by_user(user_id)
    
    # Get user's groups
    user_groups = group_service.get_user_groups_with_stats(user_id, limit=10)
    
    # Get recent jobs for user's tradesmen
    recent_jobs = job_service.get_recent_completed_jobs_for_user(user_id, limit=5)
    
    # Get statistics
    stats = {
        'total_tradesmen': len(user_tradesmen),
        'total_groups': len(user_groups),
        'total_jobs': len(recent_jobs)
    }
    
    return render_template("index.html", 
                         tradesmen=user_tradesmen, 
                         my_groups=user_groups, 
                         recent_jobs=recent_jobs,
                         stats=stats)

@main_bp.route('/init_db')
def initialize_db() -> Union[str, tuple[str, int]]:
    """Initialize the database with schema."""
    from app.services.database import get_db_service
    
    config = get_config()
    db_service = get_db_service()
    schema_path = Path(__file__).parent.parent.parent / 'sql' / 'schema.sql'
    add_file_fields_path = Path(__file__).parent.parent.parent / 'sql' / 'add_file_fields.sql'
    
    try:
        with open(schema_path, 'r') as f:
            db_service.get_connection().cursor().executescript(f.read())
        with open(add_file_fields_path, 'r') as f:
            db_service.get_connection().cursor().executescript(f.read())
        return 'Database initialized successfully.'
    except Exception as e:
        return f'Error initializing database: {e}', 500

@main_bp.route('/uploads/<path:filename>')
@login_required
def uploaded_file(filename):
    """Serve uploaded files."""
    from flask import send_from_directory
    
    # Security check - ensure filename doesn't contain path traversal
    if '..' in filename or filename.startswith('/'):
        abort(404)
    
    upload_folder = current_app.config['UPLOAD_FOLDER']
    return send_from_directory(upload_folder, filename)

 