from flask import Blueprint, flash, redirect, render_template, request, session, url_for, g
from helpers import login_required
from app.services.user_service import UserService
from app.services.tradesman_service import TradesmanService
from app.services.job_service import JobService
from app.services.group_service import GroupService

# Create Blueprint
main_bp = Blueprint('main', __name__)

# Initialize services
user_service = UserService()
tradesman_service = TradesmanService()
job_service = JobService()
group_service = GroupService()

@main_bp.route("/")
@login_required
def index():
    """Show index"""
    if session.get("user_id"):
        user_id = session["user_id"]
        
        # Get user information
        user = user_service.get_user_by_id(user_id)
        username = user["username"] if user else "Unknown"

        # Get top-rated tradesmen accessible to user
        tradesmen = tradesman_service.get_top_rated_tradesmen_for_user(user_id, limit=10)
        
        # Get recently completed jobs
        recent_jobs = job_service.get_recent_completed_jobs_for_user(user_id, limit=10)
        
        # Get user's groups
        my_groups = group_service.get_user_groups_with_stats(user_id, limit=5)
        
        return render_template("index.html", 
                             username=username, 
                             tradesmen=tradesmen,
                             recent_jobs=recent_jobs,
                             my_groups=my_groups)
    else:
        return redirect("/login")

@main_bp.route('/init_db')
def initialize_db():
    init_db()
    return 'Database initialized.'

def init_db():
    import app
    with app.app.app_context():
        from app.services.database import get_db_service
        db_service = get_db_service()
        with app.app.open_resource('sql/schema.sql', mode='r') as f:
            db_service.get_connection().cursor().executescript(f.read())
        db_service.commit()

# Legacy get_db function for backward compatibility
def get_db():
    from app.services.database import get_db_service
    return get_db_service().get_connection() 