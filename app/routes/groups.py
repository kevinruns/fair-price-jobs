from flask import Blueprint, flash, redirect, render_template, request, session, url_for
import sqlite3

from helpers import login_required

# Create Blueprint
groups_bp = Blueprint('groups', __name__)

@groups_bp.route("/create_group", methods=["GET", "POST"])
@login_required
def create_group():
    if request.method == "POST":
        group_name = request.form.get("group_name")
        group_postcode = request.form.get("group_postcode")
        
        if not group_name or not group_postcode:
            flash("Please provide both group name and postcode", "error")
            return render_template("create_group.html")
        
        db = get_db()
        try:
            # Start a transaction
            with db:
                # Insert the new group
                cursor = db.execute("INSERT INTO groups (name, postcode) VALUES (?, ?)", 
                                    (group_name, group_postcode))
                group_id = cursor.lastrowid  # Get the ID of the newly created group
                
                # Add the current user to the group
                user_id = session.get("user_id")
                db.execute("INSERT INTO user_groups (user_id, group_id, status) VALUES (?, ?, ?)",
                           (user_id, group_id, "creator"))
            
            flash("Group created successfully and you've been added to it!", "success")
            return redirect(url_for("index"))
        except sqlite3.Error as e:
            flash(f"An error occurred: {e}", "error")
            return render_template("create_group.html")
    
    return render_template("create_group.html")

@groups_bp.route("/search_groups", methods=["GET", "POST"])
@login_required
def search_groups():
    groups = []
    postcode = ""
    
    user_id = session.get("user_id")
    db = get_db()
    
    if request.method == "POST":
        postcode = request.form.get("postcode", "").strip()
        
        # Base query for search results
        query = """
            SELECT g.*, 
                   (SELECT COUNT(*) FROM user_groups WHERE group_id = g.id) as member_count,
                   CASE 
                       WHEN ug.status IS NOT NULL THEN ug.status 
                       ELSE NULL 
                   END as status
            FROM groups g 
            LEFT JOIN user_groups ug ON g.id = ug.group_id AND ug.user_id = ?
        """
        
        # Add WHERE clause only if postcode is provided
        if postcode:
            query += " WHERE g.postcode LIKE ?"
            params = (user_id, f"%{postcode}%")
        else:
            params = (user_id,)
            
        query += " GROUP BY g.id"
        
        groups = db.execute(query, params).fetchall()
        
    return render_template("search_groups.html", 
                         groups=groups, 
                         postcode=postcode)

@groups_bp.route("/view_group/<int:group_id>", methods=['GET', 'POST'])
@login_required
def view_group(group_id):
    db = get_db()
    cursor = db.cursor()
    user_id = session["user_id"]
    session['group_id'] = group_id

    # Handle POST request (button submission)
    if request.method == 'POST':
        try:
            # Instead of join_requests, directly update user_groups
            cursor.execute("INSERT INTO user_groups (user_id, group_id, status) VALUES (?, ?, 'pending')", 
                           (user_id, group_id))
            db.commit()
            flash("Join request sent successfully!", "success")
        except sqlite3.IntegrityError:
            flash("You have already requested to join this group.", "warning")
        except Exception as e:
            db.rollback()
            flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('groups.view_group', group_id=group_id))

    # Fetch group information
    cursor.execute("SELECT * FROM groups WHERE id = ?", (group_id,))
    group = cursor.fetchone()

    if group:
        group = dict(zip([column[0] for column in cursor.description], group))
        
        # Check if the user is a member of the group
        cursor.execute("SELECT 1 FROM user_groups WHERE user_id = ? AND group_id = ? AND status != 'pending'", (user_id, group_id))
        is_member = cursor.fetchone() is not None

        # Check for pending join request
        cursor.execute("SELECT status FROM user_groups WHERE user_id = ? AND group_id = ?", (user_id, group_id))
        user_group_status = cursor.fetchone()
        pending_request = user_group_status is not None and user_group_status['status'] == 'pending'

        # Fetch member count
        cursor.execute("SELECT COUNT(*) FROM user_groups WHERE group_id = ? AND status != 'pending'", (group_id,))
        member_count = cursor.fetchone()[0]

        group['member_count'] = member_count

        # Fetch pending request count for this group
        cursor.execute("SELECT COUNT(*) FROM user_groups WHERE group_id = ? AND status = 'pending'", (group_id,))
        pending_requests_count = cursor.fetchone()[0]

        # Check if user is admin/creator of this group
        cursor.execute("SELECT status FROM user_groups WHERE user_id = ? AND group_id = ?", (user_id, group_id))
        user_status = cursor.fetchone()
        is_admin_or_creator = user_status and user_status['status'] in ['admin', 'creator']

        # Fetch tradesmen for this group, sorted by trade
        cursor.execute("""
            SELECT t.* 
            FROM tradesmen t
            JOIN group_tradesmen gt ON t.id = gt.tradesman_id
            WHERE gt.group_id = ?
            ORDER BY t.trade, t.family_name
        """, (group_id,))
        tradesmen = cursor.fetchall()

        # Convert tradesmen to a list of dictionaries for easier handling in the template
        tradesmen = [dict(zip([column[0] for column in cursor.description], row)) for row in tradesmen]

        return render_template("view_group.html", 
                            group=group, 
                            is_member=is_member,
                            pending_request=pending_request,
                            tradesmen=tradesmen,
                            pending_requests_count=pending_requests_count,
                            is_admin_or_creator=is_admin_or_creator)
    else:
        flash("Group not found.", "error")
        return redirect(url_for("groups.search_groups"))

@groups_bp.route("/view_requests/<int:group_id>")
@login_required
def view_requests(group_id):
    db = get_db()
    
    # Fetch the group name separately
    group = db.execute("""
        SELECT name FROM groups WHERE id = ?
    """, (group_id,)).fetchone()
    
    # Fetch the requests
    requests = db.execute("""
        SELECT u.username, u.email, ug.id  -- Include request ID in the selection
        FROM user_groups ug
        JOIN users u ON ug.user_id = u.id
        WHERE ug.group_id = ? AND ug.status = 'pending'
    """, (group_id,)).fetchall()
    
    # If no pending requests, redirect to group page
    if not requests:
        flash("No pending requests found.", "info")
        return redirect(url_for('groups.view_group', group_id=group_id))
    
    return render_template("view_requests.html", requests=requests, group_name=group['name'])

@groups_bp.route("/view_all_pending_requests")
@login_required
def view_all_pending_requests():
    """Show all pending requests for groups where user is admin/creator"""
    db = get_db()
    
    # Fetch all pending requests for groups where user is admin/creator
    requests = db.execute("""
        SELECT g.name as group_name, g.id as group_id, u.username, u.email, ug.id as request_id
        FROM user_groups ug1
        JOIN user_groups ug ON ug1.group_id = ug.group_id
        JOIN groups g ON ug.group_id = g.id
        JOIN users u ON ug.user_id = u.id
        WHERE ug1.user_id = ? 
        AND ug1.status IN ('admin', 'creator')
        AND ug.status = 'pending'
        ORDER BY g.name, u.username
    """, (session["user_id"],)).fetchall()
    
    return render_template("view_all_pending_requests.html", requests=requests)

@groups_bp.route('/handle_request/<int:request_id>/<action>', methods=['POST'])
@login_required
def handle_request(request_id, action):
    db = get_db()
    
    # Get the request details
    request_data = db.execute("SELECT user_id, group_id FROM user_groups WHERE id = ?", (request_id,)).fetchone()
    
    if action == 'accept':
        if request_data:
            user_id = request_data['user_id']
            group_id = request_data['group_id']
            
            # Update user_groups table to set status to 'member'
            db.execute("UPDATE user_groups SET status = 'member' WHERE user_id = ? AND group_id = ?", (user_id, group_id))
            
            flash('Request accepted and user added to the group.', 'success')
        else:
            flash('Request not found.', 'danger')
    
    elif action == 'reject':
        # Remove the request from user_groups table
        db.execute("DELETE FROM user_groups WHERE id = ?", (request_id,))
        db.commit()
        flash('Request rejected.', 'info')
    
    return redirect(url_for('groups.view_requests', group_id=request_data['group_id']))

@groups_bp.route("/group_members/<int:group_id>")
@login_required
def group_members(group_id):
    db = get_db()
    members = db.execute("""
        SELECT u.username, u.firstname, u.lastname, u.email 
        FROM user_groups ug
        JOIN users u ON ug.user_id = u.id
        WHERE ug.group_id = ?
    """, (group_id,)).fetchall()

    group_name_result = db.execute("""
        SELECT name 
        FROM groups 
        WHERE id = ?
    """, (group_id,)).fetchone()

    group_name = group_name_result['name'] if group_name_result else "Unknown Group"  # Default if not found

    return render_template("group_members.html", members=members, group_id=group_id, group_name=group_name)

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