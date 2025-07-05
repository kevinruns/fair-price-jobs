from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from helpers import login_required
from app.services.user_service import UserService
from app.services.group_service import GroupService
from app.services.tradesman_service import TradesmanService
from app.services.job_service import JobService
from config import get_config

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
@login_required
def index():
    """Show portfolio of tradesmen and recent jobs."""
    user_service = UserService()
    group_service = GroupService()
    tradesman_service = TradesmanService()
    job_service = JobService()
    
    user_id = session.get("user_id")
    
    # Get user's tradesmen
    user_tradesmen = tradesman_service.get_user_tradesmen(user_id)
    
    # Get user's groups
    user_groups = group_service.get_user_groups(user_id)
    
    # Get recent jobs for user's tradesmen
    recent_jobs = job_service.get_recent_jobs_for_user(user_id, limit=5)
    
    # Get statistics
    stats = {
        'total_tradesmen': len(user_tradesmen),
        'total_groups': len(user_groups),
        'total_jobs': len(recent_jobs)
    }
    
    return render_template("index.html", 
                         tradesmen=user_tradesmen, 
                         groups=user_groups, 
                         recent_jobs=recent_jobs,
                         stats=stats)

@main_bp.route('/init_db')
def initialize_db():
    """Initialize the database with schema."""
    from app.services.database import get_db_service
    from pathlib import Path
    
    config = get_config()
    db_service = get_db_service()
    schema_path = Path(__file__).parent.parent.parent / 'sql' / 'schema.sql'
    
    try:
        with open(schema_path, 'r') as f:
            db_service.get_connection().cursor().executescript(f.read())
        return 'Database initialized successfully.'
    except Exception as e:
        return f'Error initializing database: {e}', 500

 