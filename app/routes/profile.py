from flask import Blueprint, flash, redirect, render_template, request, session, url_for
import sqlite3

from helpers import login_required

# Create Blueprint
profile_bp = Blueprint('profile', __name__)

@profile_bp.route("/user_profile/<int:user_id>")
@login_required
def user_profile(user_id):
    """Show user profile with basic information"""
    db = get_db()
    cursor = db.cursor()

    # Get user information
    cursor.execute("SELECT id, username, firstname, lastname, email, postcode FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("index"))

    # Get tradesmen count for this user
    cursor.execute("SELECT COUNT(*) as tradesmen_count FROM user_tradesmen WHERE user_id = ?", (user_id,))
    tradesmen_count = cursor.fetchone()['tradesmen_count']

    # Get groups count for this user
    cursor.execute("SELECT COUNT(*) as groups_count FROM user_groups WHERE user_id = ? AND status != 'pending'", (user_id,))
    groups_count = cursor.fetchone()['groups_count']

    return render_template("user_profile.html", 
                         user=dict(user),
                         tradesmen_count=tradesmen_count,
                         groups_count=groups_count)

@profile_bp.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    """Edit current user's profile"""
    db = get_db()
    cursor = db.cursor()
    user_id = session["user_id"]

    if request.method == "POST":
        # Get form data
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        email = request.form.get("email")
        postcode = request.form.get("postcode")

        # Basic validation
        if not all([firstname, lastname, email, postcode]):
            flash("All fields are required.", "error")
            return redirect(url_for("profile.edit_profile"))

        try:
            # Update user profile
            cursor.execute("""
                UPDATE users 
                SET firstname = ?, lastname = ?, email = ?, postcode = ?
                WHERE id = ?
            """, (firstname, lastname, email, postcode, user_id))
            
            db.commit()
            flash("Profile updated successfully!", "success")
            return redirect(url_for("profile.user_profile", user_id=user_id))
        except Exception as e:
            db.rollback()
            flash(f"An error occurred: {str(e)}", "error")
            return redirect(url_for("profile.edit_profile"))

    # GET request - show current user data
    cursor.execute("SELECT id, username, firstname, lastname, email, postcode FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("index"))

    return render_template("edit_profile.html", user=dict(user))

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