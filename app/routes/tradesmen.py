from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from helpers import login_required
from app.services.tradesman_service import TradesmanService

# Create Blueprint
tradesmen_bp = Blueprint('tradesmen', __name__)

# Initialize service
tradesman_service = TradesmanService()

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

        try:
            tradesman_id = tradesman_service.create_tradesman(
                trade, first_name, family_name, company_name, address, postcode, phone_number, email
            )
            # Create the user-tradesman relationship
            tradesman_service.add_user_tradesman_relationship(session["user_id"], tradesman_id)
            flash("Tradesman added successfully!", "success")
            return redirect(url_for("tradesmen.view_tradesman", tradesman_id=tradesman_id))
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")
            return redirect(url_for("tradesmen.add_tradesman"))

    # If it's a GET request, just render the form
    return render_template("add_tradesman.html")

@tradesmen_bp.route("/tradesman/<int:tradesman_id>")
@login_required
def view_tradesman(tradesman_id):
    try:
        tradesman = tradesman_service.get_tradesman_by_id(tradesman_id)
        if not tradesman:
            flash("Tradesman not found.", "error")
            return redirect(url_for("groups.search_groups"))

        jobs = tradesman_service.get_tradesman_jobs(tradesman_id)
        quotes = tradesman_service.get_tradesman_quotes(tradesman_id)
        group_id = session.get('group_id')
        added_by_info = tradesman_service.get_tradesman_added_by_info(tradesman_id)
        can_edit = tradesman_service.can_user_edit_tradesman(session["user_id"], tradesman_id)

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
    # Check if the tradesman exists and belongs to the current user
    can_edit = tradesman_service.can_user_edit_tradesman(session["user_id"], tradesman_id)
    tradesman = tradesman_service.get_tradesman_by_id(tradesman_id)
    if not tradesman or not can_edit:
        flash("Tradesman not found or you don't have permission to edit.", "error")
        return redirect(url_for("main.index"))

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
            tradesman_service.update_tradesman(
                tradesman_id,
                trade=trade,
                first_name=first_name,
                family_name=family_name,
                company_name=company_name,
                address=address,
                postcode=postcode,
                phone_number=phone_number,
                email=email
            )
            flash("Tradesman updated successfully!", "success")
            return redirect(url_for("tradesmen.view_tradesman", tradesman_id=tradesman_id))
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")
            return redirect(url_for("tradesmen.edit_tradesman", tradesman_id=tradesman_id))

    # If it's a GET request, render the form with current tradesman data
    return render_template("edit_tradesman.html", tradesman=tradesman)

@tradesmen_bp.route("/user_tradesmen/<int:user_id>")
@login_required
def user_tradesmen(user_id):
    """Show tradesmen associated with a specific user"""
    # Get user information and tradesmen
    from app.services.user_service import UserService
    user_service = UserService()
    user = user_service.get_user_by_id(user_id)
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("main.index"))
    tradesmen_list = tradesman_service.get_tradesmen_by_user(user_id)
    return render_template("user_tradesmen.html", user=user, tradesmen=tradesmen_list)

@tradesmen_bp.route("/add_my_tradesman_to_group/<int:group_id>", methods=["GET", "POST"])
@login_required
def add_my_tradesman_to_group(group_id):
    """Show user's tradesmen and allow adding them to a group"""
    from app.services.group_service import GroupService
    group_service = GroupService()
    # Check if user is a member of the group
    membership = group_service.get_user_group_membership(session["user_id"], group_id)
    if not membership or membership['status'] not in ['member', 'admin', 'creator']:
        flash("You must be a member of this group to add tradesmen.", "error")
        return redirect(url_for("groups.view_group", group_id=group_id))
    group = group_service.get_group_by_id(group_id)
    if not group:
        flash("Group not found.", "error")
        return redirect(url_for("main.index"))
    if request.method == "POST":
        tradesman_id = request.form.get("tradesman_id")
        if tradesman_id:
            try:
                if tradesman_service.is_tradesman_in_group(group_id, tradesman_id):
                    flash("This tradesman is already in the group.", "info")
                else:
                    tradesman_service.add_tradesman_to_group(group_id, tradesman_id)
                    flash("Tradesman added to group successfully!", "success")
            except Exception as e:
                flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for("tradesmen.add_my_tradesman_to_group", group_id=group_id))
    # GET request - show user's tradesmen
    user_tradesmen = tradesman_service.get_tradesmen_by_user(session["user_id"])
    # Mark which are already in the group
    for t in user_tradesmen:
        t['in_group'] = tradesman_service.is_tradesman_in_group(group_id, t['id'])
    return render_template("add_my_tradesman_to_group.html", user_tradesmen=user_tradesmen, group=group)

 