from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from helpers import login_required
from app.services.user_service import UserService

# Create Blueprint
profile_bp = Blueprint('profile', __name__)

# Initialize service
user_service = UserService()

@profile_bp.route("/user_profile/<int:user_id>")
@login_required
def user_profile(user_id):
    """Show user profile with basic information"""
    # Get user information
    user = user_service.get_user_by_id(user_id)
    
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("main.index"))

    # Get user statistics
    user_groups = user_service.get_user_groups(user_id)
    user_tradesmen = user_service.get_user_tradesmen(user_id)
    
    tradesmen_count = len(user_tradesmen)
    groups_count = len([g for g in user_groups if g['status'] != 'pending'])

    return render_template("user_profile.html", 
                         user=user,
                         tradesmen_count=tradesmen_count,
                         groups_count=groups_count)

@profile_bp.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    """Edit current user's profile"""
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
            if user_service.update_user(user_id, 
                                      firstname=firstname, 
                                      lastname=lastname, 
                                      email=email, 
                                      postcode=postcode):
                flash("Profile updated successfully!", "success")
                return redirect(url_for("profile.user_profile", user_id=user_id))
            else:
                flash("Failed to update profile.", "error")
                return redirect(url_for("profile.edit_profile"))
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")
            return redirect(url_for("profile.edit_profile"))

    # GET request - show current user data
    user = user_service.get_user_by_id(user_id)
    
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("main.index"))

    return render_template("edit_profile.html", user=user)

 