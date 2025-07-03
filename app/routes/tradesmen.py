from flask import Blueprint, flash, redirect, render_template, request, session, url_for
import sqlite3

from helpers import login_required

# Create Blueprint
tradesmen_bp = Blueprint('tradesmen', __name__)

@tradesmen_bp.route("/add_tradesman", methods=["GET", "POST"])
@login_required
def add_tradesman():
    if request.method == "POST":
        # Get form data
        trade = request.form.get("trade")
        first_name = request.form.get("first_name")
        family_name = request.form.get("family_name")
        company_name = request.form.get("company_name")
        address = request.form.get("address")
        postcode = request.form.get("postcode")
        phone_number = request.form.get("phone_number")
        email = request.form.get("email")

        db = get_db()
        cursor = db.cursor()

        # Insert the tradesman into the database
        try:
            cursor.execute("""
                INSERT INTO tradesmen (
                    trade, first_name, family_name, company_name, 
                    address, postcode, phone_number, email
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                trade, first_name, family_name, company_name,
                address, postcode, phone_number, email
            ))
            
            tradesman_id = cursor.lastrowid  # Get the ID of the newly inserted tradesman
            
            # Create the user-tradesman relationship
            cursor.execute("""
                INSERT INTO user_tradesmen (user_id, tradesman_id)
                VALUES (?, ?)
            """, (session["user_id"], tradesman_id))
            
            db.commit()
            flash("Tradesman added successfully!", "success")
            return redirect(url_for("tradesmen.view_tradesman", tradesman_id=tradesman_id))
        except Exception as e:
            db.rollback()
            flash(f"An error occurred: {str(e)}", "error")
            return redirect(url_for("tradesmen.add_tradesman"))

    # If it's a GET request, just render the form
    return render_template("add_tradesman.html")

@tradesmen_bp.route("/tradesman/<int:tradesman_id>")
@login_required
def view_tradesman(tradesman_id):
    try:
        db = get_db()
        cursor = db.cursor()

        # Fetch tradesman details
        cursor.execute("SELECT * FROM tradesmen WHERE id = ?", (tradesman_id,))
        tradesman = cursor.fetchone()

        if not tradesman:
            flash("Tradesman not found.", "error")
            return redirect(url_for("groups.search_groups"))

        # Convert tradesman to a dictionary
        tradesman = dict(zip([column[0] for column in cursor.description], tradesman))

        # Fetch jobs for this tradesman
        cursor.execute("""
            SELECT id, date_started, date_finished, title, description, total_cost, rating
            FROM jobs
            WHERE tradesman_id = ? AND type = 'job'
            ORDER BY date_finished DESC
        """, (tradesman_id,))
        jobs = cursor.fetchall()

        # Convert jobs to dictionaries for easier handling in the template
        jobs = [dict(zip([column[0] for column in cursor.description], row)) for row in jobs]

        # Fetch quotes for this tradesman (excluding accepted quotes)
        cursor.execute("""
            SELECT id, date_requested, date_received, title, description, total_quote, status
            FROM jobs
            WHERE tradesman_id = ? AND type = 'quote' AND status != 'accepted'
            ORDER BY date_received DESC
        """, (tradesman_id,))
        quotes = cursor.fetchall()

        # Convert quotes to dictionaries for easier handling in the template
        quotes = [dict(zip([column[0] for column in cursor.description], row)) for row in quotes]

        group_id = session.get('group_id')

        # Check if current user is the one who added this tradesman and get added by info
        cursor.execute("""
            SELECT DATE(ut.date_added) as date_added, u.username, u.firstname, u.lastname
            FROM user_tradesmen ut
            JOIN users u ON ut.user_id = u.id
            WHERE ut.tradesman_id = ?
            ORDER BY ut.date_added ASC
            LIMIT 1
        """, (tradesman_id,))
        added_by_info = cursor.fetchone()
        
        # Convert added_by_info to dictionary if it exists
        if added_by_info:
            added_by_info = dict(zip([column[0] for column in cursor.description], added_by_info))
        
        # Check if current user is the one who added this tradesman
        cursor.execute("""
            SELECT 1 FROM user_tradesmen 
            WHERE user_id = ? AND tradesman_id = ?
        """, (session["user_id"], tradesman_id))
        can_edit = cursor.fetchone() is not None

        return render_template("view_tradesman.html", 
                             tradesman=tradesman, 
                             jobs=jobs,
                             quotes=quotes,
                             group_id=group_id,
                             can_edit=can_edit,
                             added_by_info=added_by_info)
    
    except Exception as e:
        flash(f"An error occurred while fetching tradesman data: {str(e)}", "error")
        return redirect(url_for("groups.search_groups"))

@tradesmen_bp.route("/edit_tradesman/<int:tradesman_id>", methods=["GET", "POST"])
@login_required
def edit_tradesman(tradesman_id):
    db = get_db()
    cursor = db.cursor()

    # Check if the tradesman exists and belongs to the current user
    cursor.execute("""
        SELECT t.* 
        FROM tradesmen t
        JOIN user_tradesmen ut ON t.id = ut.tradesman_id
        WHERE t.id = ? AND ut.user_id = ?
    """, (tradesman_id, session["user_id"]))
    tradesman = cursor.fetchone()

    if not tradesman:
        flash("Tradesman not found or you don't have permission to edit.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        # Get form data
        trade = request.form.get("trade")
        first_name = request.form.get("first_name")
        family_name = request.form.get("family_name")
        company_name = request.form.get("company_name")
        address = request.form.get("address")
        postcode = request.form.get("postcode")
        phone_number = request.form.get("phone_number")
        email = request.form.get("email")

        try:
            # Update the tradesman
            cursor.execute("""
                UPDATE tradesmen 
                SET trade = ?, first_name = ?, family_name = ?, company_name = ?, 
                    address = ?, postcode = ?, phone_number = ?, email = ?
                WHERE id = ?
            """, (trade, first_name, family_name, company_name, 
                  address, postcode, phone_number, email, tradesman_id))
            
            db.commit()
            flash("Tradesman updated successfully!", "success")
            return redirect(url_for("tradesmen.view_tradesman", tradesman_id=tradesman_id))
        except Exception as e:
            db.rollback()
            flash(f"An error occurred: {str(e)}", "error")
            return redirect(url_for("tradesmen.edit_tradesman", tradesman_id=tradesman_id))

    # If it's a GET request, render the form with current tradesman data
    return render_template("edit_tradesman.html", tradesman=dict(tradesman))

@tradesmen_bp.route("/user_tradesmen/<int:user_id>")
@login_required
def user_tradesmen(user_id):
    """Show tradesmen associated with a specific user"""
    db = get_db()
    cursor = db.cursor()

    # Get user information
    cursor.execute("SELECT username, firstname, lastname FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("index"))

    # Get tradesmen associated with this user
    cursor.execute("""
        SELECT t.*, 
               COUNT(j.id) as job_count,
               AVG(j.rating) as avg_rating,
               ut.date_added
        FROM tradesmen t
        JOIN user_tradesmen ut ON t.id = ut.tradesman_id
        LEFT JOIN jobs j ON t.id = j.tradesman_id
        WHERE ut.user_id = ?
        GROUP BY t.id
        ORDER BY t.trade, t.family_name, t.first_name, t.company_name
    """, (user_id,))
    tradesmen = cursor.fetchall()

    # Convert to list of dictionaries
    tradesmen_list = [dict(row) for row in tradesmen]

    return render_template("user_tradesmen.html", 
                         user=dict(user),
                         tradesmen=tradesmen_list)

@tradesmen_bp.route("/add_my_tradesman_to_group/<int:group_id>", methods=["GET", "POST"])
@login_required
def add_my_tradesman_to_group(group_id):
    """Show user's tradesmen and allow adding them to a group"""
    db = get_db()
    cursor = db.cursor()
    
    # Check if user is a member of the group
    cursor.execute("""
        SELECT status FROM user_groups 
        WHERE user_id = ? AND group_id = ?
    """, (session["user_id"], group_id))
    membership = cursor.fetchone()
    
    if not membership or membership['status'] not in ['member', 'admin', 'creator']:
        flash("You must be a member of this group to add tradesmen.", "error")
        return redirect(url_for("groups.view_group", group_id=group_id))
    
    # Get group information
    cursor.execute("SELECT * FROM groups WHERE id = ?", (group_id,))
    group = cursor.fetchone()
    
    if not group:
        flash("Group not found.", "error")
        return redirect(url_for("index"))
    
    if request.method == "POST":
        tradesman_id = request.form.get("tradesman_id")
        
        if tradesman_id:
            try:
                # Check if tradesman is already in the group
                cursor.execute("""
                    SELECT 1 FROM group_tradesmen 
                    WHERE group_id = ? AND tradesman_id = ?
                """, (group_id, tradesman_id))
                
                if cursor.fetchone():
                    flash("This tradesman is already in the group.", "info")
                else:
                    # Add tradesman to group
                    cursor.execute("""
                        INSERT INTO group_tradesmen (group_id, tradesman_id)
                        VALUES (?, ?)
                    """, (group_id, tradesman_id))
                    
                    db.commit()
                    flash("Tradesman added to group successfully!", "success")
                
            except Exception as e:
                db.rollback()
                flash(f"An error occurred: {str(e)}", "error")
        
        return redirect(url_for("tradesmen.add_my_tradesman_to_group", group_id=group_id))
    
    # GET request - show user's tradesmen
    cursor.execute("""
        SELECT t.*, 
               CASE WHEN gt.tradesman_id IS NOT NULL THEN 1 ELSE 0 END as in_group
        FROM tradesmen t
        JOIN user_tradesmen ut ON t.id = ut.tradesman_id
        LEFT JOIN group_tradesmen gt ON t.id = gt.tradesman_id AND gt.group_id = ?
        WHERE ut.user_id = ?
        ORDER BY t.family_name, t.first_name, t.company_name
    """, (group_id, session["user_id"]))
    
    user_tradesmen = cursor.fetchall()
    user_tradesmen = [dict(row) for row in user_tradesmen]
    
    return render_template("add_my_tradesman_to_group.html", 
                         user_tradesmen=user_tradesmen,
                         group=dict(group))

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