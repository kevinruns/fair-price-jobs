from flask import Blueprint, flash, redirect, render_template, request, session, url_for, g
import sqlite3

from helpers import login_required

# Create Blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route("/")
@login_required
def index():
    """Show index"""
    if session.get("user_id"):
        db = get_db()
        cursor = db.cursor()
        
        # Fetch the username
        cursor.execute("SELECT username FROM users WHERE id = ?", (session["user_id"],))
        user = cursor.fetchone()
        username = user["username"] if user else "Unknown"
        user_id = session["user_id"]

        # Fetch top-rated tradesmen (accessible to user through their groups or direct ownership)
        tradesmen = db.execute("""
            SELECT t.*, 
                   COUNT(CASE WHEN j.type = 'job' THEN j.id END) as job_count,
                   AVG(CASE WHEN j.type = 'job' THEN j.rating END) as avg_rating,
                   u.username as added_by_username,
                   u.id as added_by_user_id,
                   CASE WHEN ut.user_id = ? THEN 1 ELSE 0 END as is_my_tradesman
            FROM tradesmen t
            JOIN user_tradesmen ut ON t.id = ut.tradesman_id
            LEFT JOIN jobs j ON t.id = j.tradesman_id
            JOIN users u ON ut.user_id = u.id
            WHERE ut.user_id = ? OR ut.user_id IN (
                SELECT DISTINCT ug2.user_id 
                FROM user_groups ug1
                JOIN user_groups ug2 ON ug1.group_id = ug2.group_id
                WHERE ug1.user_id = ? AND ug1.status IN ('member', 'admin', 'creator')
            )
            GROUP BY t.id
            ORDER BY AVG(CASE WHEN j.type = 'job' THEN j.rating END) DESC NULLS LAST, COUNT(CASE WHEN j.type = 'job' THEN j.id END) DESC
            LIMIT 10
        """, (user_id, user_id, user_id)).fetchall()
        
        # Convert tradesmen to list of dicts
        tradesmen_list = [dict(row) for row in tradesmen]
        
        # Fetch recently completed jobs (added by user or users in groups where user is a member)
        recent_jobs = db.execute("""
            SELECT j.*, 
                   t.first_name, t.family_name, t.company_name, t.trade,
                   u.username as added_by_username,
                   u.id as added_by_user_id,
                   g.name as group_name,
                   g.id as group_id
            FROM jobs j
            JOIN tradesmen t ON j.tradesman_id = t.id
            JOIN users u ON j.user_id = u.id
            LEFT JOIN user_groups ug ON u.id = ug.user_id
            LEFT JOIN groups g ON ug.group_id = g.id
            WHERE (j.user_id = ? OR 
                   (ug.group_id IN (
                       SELECT group_id FROM user_groups 
                       WHERE user_id = ? AND status IN ('member', 'admin', 'creator')
                   )))
            AND j.date_finished IS NOT NULL
            ORDER BY j.date_finished DESC
            LIMIT 10
        """, (user_id, user_id)).fetchall()
        
        # Convert jobs to list of dicts
        recent_jobs_list = [dict(row) for row in recent_jobs]
        
        # Fetch user's groups
        my_groups = db.execute("""
            SELECT g.*, 
                   (SELECT COUNT(*) FROM user_groups WHERE group_id = g.id AND status != 'pending') as member_count,
                   ug.status
            FROM groups g
            JOIN user_groups ug ON g.id = ug.group_id
            WHERE ug.user_id = ? AND ug.status != 'pending'
            ORDER BY g.name
            LIMIT 5
        """, (user_id,)).fetchall()
        
        # Convert groups to list of dicts
        my_groups_list = [dict(row) for row in my_groups]
        
        return render_template("index.html", 
                             username=username, 
                             tradesmen=tradesmen_list,
                             recent_jobs=recent_jobs_list,
                             my_groups=my_groups_list)
    else:
        return redirect("/login")

@main_bp.route('/init_db')
def initialize_db():
    init_db()
    return 'Database initialized.'

def init_db():
    import app
    with app.app.app_context():
        db = get_db()
        with app.app.open_resource('sql/schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# Import get_db function - this will be moved to a database service later
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        from app.config import DATABASE
        db = g._database = sqlite3.connect(DATABASE, isolation_level=None)
        db.row_factory = sqlite3.Row
    return db 