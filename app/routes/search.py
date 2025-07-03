from flask import Blueprint, flash, redirect, render_template, request, session, url_for
import sqlite3

from helpers import login_required

# Create Blueprint
search_bp = Blueprint('search', __name__)

@search_bp.route("/search_tradesmen", methods=["GET", "POST"])
@login_required
def search_tradesmen():
    """Search for tradesmen"""
    # Get message from query parameter
    message = request.args.get("message", "")
    
    if request.method == "POST":
        search_term = request.form.get("search_term", "").strip()
        trade = request.form.get("trade", "")
        postcode = request.form.get("postcode", "").strip()
        
        db = get_db()
        query = """
            SELECT DISTINCT t.*, 
                   COUNT(j.id) as job_count,
                   AVG(j.rating) as avg_rating,
                   u.username as added_by_username,
                   u.id as added_by_user_id
            FROM tradesmen t
            LEFT JOIN jobs j ON t.id = j.tradesman_id
            JOIN user_tradesmen ut ON t.id = ut.tradesman_id
            JOIN users u ON ut.user_id = u.id
            WHERE 1=1
        """
        params = []
        
        if search_term:
            query += " AND (t.first_name LIKE ? OR t.family_name LIKE ? OR t.company_name LIKE ? OR t.email LIKE ? OR t.phone_number LIKE ?)"
            search_pattern = f"%{search_term}%"
            params.extend([search_pattern, search_pattern, search_pattern, search_pattern, search_pattern])
            
        if trade:
            query += " AND t.trade = ?"
            params.append(trade)
            
        if postcode:
            query += " AND t.postcode LIKE ?"
            params.append(f"{postcode}%")
            
        query += " GROUP BY t.id ORDER BY COUNT(j.id) DESC, avg_rating DESC NULLS LAST"
        
        tradesmen = db.execute(query, params).fetchall()
        tradesmen = [dict(row) for row in tradesmen]
        
        # Get unique trades for the filter dropdown
        trades = db.execute("SELECT DISTINCT trade FROM tradesmen ORDER BY trade").fetchall()
        trades = [row['trade'] for row in trades]
        
        return render_template("search_tradesmen.html", 
                             tradesmen=tradesmen,
                             trades=trades,
                             search_term=search_term,
                             selected_trade=trade,
                             postcode=postcode,
                             message=message)
    
    # GET request - show empty search form
    db = get_db()
    trades = db.execute("SELECT DISTINCT trade FROM tradesmen ORDER BY trade").fetchall()
    trades = [row['trade'] for row in trades]
    
    return render_template("search_tradesmen.html", trades=trades, message=message)

@search_bp.route("/search_jobs", methods=["GET", "POST"])
@login_required
def search_jobs():
    """Search for jobs by keywords in title"""
    if request.method == "POST":
        search_term = request.form.get("search_term", "").strip()
        trade = request.form.get("trade", "")
        rating = request.form.get("rating", "")
        added_by_user = request.form.get("added_by_user", "")
        group = request.form.get("group", "")
        
        db = get_db()
        query = """
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
            WHERE 1=1
        """
        params = []
        
        if search_term:
            query += " AND (j.title LIKE ? OR j.description LIKE ?)"
            search_pattern = f"%{search_term}%"
            params.extend([search_pattern, search_pattern])
            
        if trade:
            query += " AND t.trade = ?"
            params.append(trade)
            
        if rating:
            query += " AND j.rating >= ?"
            params.append(int(rating))
            
        if added_by_user:
            query += " AND u.username = ?"
            params.append(added_by_user)
            
        if group:
            query += """ AND EXISTS (
                SELECT 1 FROM group_tradesmen gt 
                JOIN groups g ON gt.group_id = g.id 
                WHERE gt.tradesman_id = t.id AND g.name = ?
            )"""
            params.append(group)
            
        query += " ORDER BY j.date_finished DESC NULLS LAST"
        
        jobs = db.execute(query, params).fetchall()
        jobs = [dict(row) for row in jobs]
        
        # Get unique trades for the filter dropdown
        trades = db.execute("SELECT DISTINCT trade FROM tradesmen ORDER BY trade").fetchall()
        trades = [row['trade'] for row in trades]
        
        # Get unique users for the filter dropdown
        users = db.execute("""
            SELECT DISTINCT u.username 
            FROM users u 
            JOIN jobs j ON u.id = j.user_id 
            ORDER BY u.username
        """).fetchall()
        users = [dict(row) for row in users]
        
        # Get unique groups for the filter dropdown
        groups = db.execute("""
            SELECT DISTINCT g.name 
            FROM groups g 
            JOIN group_tradesmen gt ON g.id = gt.group_id 
            JOIN jobs j ON gt.tradesman_id = j.tradesman_id
            ORDER BY g.name
        """).fetchall()
        groups = [dict(row) for row in groups]
        
        return render_template("search_jobs.html", 
                             jobs=jobs,
                             trades=trades,
                             users=users,
                             groups=groups,
                             search_term=search_term,
                             selected_trade=trade,
                             selected_rating=rating,
                             selected_user=added_by_user,
                             selected_group=group)
    
    # GET request - show empty search form
    db = get_db()
    trades = db.execute("SELECT DISTINCT trade FROM tradesmen ORDER BY trade").fetchall()
    trades = [row['trade'] for row in trades]
    
    # Get unique users for the filter dropdown
    users = db.execute("""
        SELECT DISTINCT u.username 
        FROM users u 
        JOIN jobs j ON u.id = j.user_id 
        ORDER BY u.username
    """).fetchall()
    users = [dict(row) for row in users]
    
    # Get unique groups for the filter dropdown
    groups = db.execute("""
        SELECT DISTINCT g.name 
        FROM groups g 
        JOIN group_tradesmen gt ON g.id = gt.group_id 
        JOIN jobs j ON gt.tradesman_id = j.tradesman_id
        ORDER BY g.name
    """).fetchall()
    groups = [dict(row) for row in groups]
    
    return render_template("search_jobs.html", 
                         trades=trades,
                         users=users,
                         groups=groups)

# Import get_db function - this will be moved to a database service later
def get_db():
    from flask import g
    db = getattr(g, '_database', None)
    if db is None:
        from app.config import DATABASE
        import sqlite3
        db = g._database = sqlite3.connect(DATABASE, isolation_level=None)
        db.row_factory = sqlite3.Row
    return db 