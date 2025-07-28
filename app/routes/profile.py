from flask import Blueprint, render_template, session, flash, redirect, url_for, request
from werkzeug.wrappers.response import Response
from typing import Any, Dict, List, Optional, Union
from app.helpers import login_required
from app.services.user_service import UserService
from app.services.group_service import GroupService
from app.services.tradesman_service import TradesmanService
from app.services.job_service import JobService

profile_bp = Blueprint('profile', __name__)

user_service = UserService()
group_service = GroupService()
tradesman_service = TradesmanService()
job_service = JobService()

@profile_bp.route('/profile')
@login_required
def profile() -> Union[str, Response]:
    user_id = session.get('user_id')
    if user_id is None:
        flash('User not logged in.', 'error')
        return redirect(url_for('auth.login'))
    user = user_service.get_user_by_id(user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('auth.login'))
    user_groups = group_service.get_user_groups(user_id)
    user_tradesmen = tradesman_service.get_tradesmen_by_user(user_id)
    user_jobs = job_service.get_jobs_by_user(user_id)
    return render_template('profile.html', user=user, groups=user_groups, tradesmen=user_tradesmen, jobs=user_jobs)

@profile_bp.route("/user_profile/<int:user_id>")
@login_required
def user_profile(user_id: int) -> Union[str, Response]:
    """Show user profile with basic information"""
    # Get user information
    user = user_service.get_user_by_id(user_id)
    
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("main.index"))

    # Get user statistics
    user_groups = group_service.get_user_groups(user_id)
    user_tradesmen = tradesman_service.get_tradesmen_by_user(user_id)
    
    tradesmen_count = len(user_tradesmen)
    groups_count = len([g for g in user_groups if g['status'] != 'pending'])

    return render_template("user_profile.html", 
                         user=user,
                         tradesmen_count=tradesmen_count,
                         groups_count=groups_count)

@profile_bp.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile() -> Union[str, Response]:
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

 