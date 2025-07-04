from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from helpers import login_required
from app.services.job_service import JobService
from app.services.tradesman_service import TradesmanService

# Create Blueprint
jobs_bp = Blueprint('jobs', __name__)

# Initialize services
job_service = JobService()
tradesman_service = TradesmanService()

@jobs_bp.route("/add_job/<int:tradesman_id>", methods=["GET", "POST"])
@login_required
def add_job(tradesman_id):
    # Get tradesman information
    tradesman = tradesman_service.get_tradesman_by_id(tradesman_id)
    
    if not tradesman:
        flash("Tradesman not found.", "error")
        return redirect(url_for("search.search_tradesmen"))

    if request.method == "POST":
        user_id = session["user_id"]
        date_started = request.form.get("date_started")
        date_finished = request.form.get("date_finished")
        title = request.form.get("title")
        description = request.form.get("description")
        call_out_fee = request.form.get("call_out_fee")
        materials_fee = request.form.get("materials_fee")
        hourly_rate = request.form.get("hourly_rate")
        hours_worked = request.form.get("hours_worked")
        daily_rate = request.form.get("daily_rate")
        days_worked = request.form.get("days_worked")
        total_cost = request.form.get("total_cost")
        rating = request.form.get("rating")

        try:
            # Convert empty strings to None for optional fields
            call_out_fee = int(call_out_fee) if call_out_fee else None
            materials_fee = int(materials_fee) if materials_fee else None
            hourly_rate = int(hourly_rate) if hourly_rate else None
            hours_worked = float(hours_worked) if hours_worked else None
            daily_rate = int(daily_rate) if daily_rate else None
            days_worked = float(days_worked) if days_worked else None
            total_cost = int(total_cost) if total_cost else None
            rating = int(rating) if rating else None
            
            job_service.create_job(
                user_id=user_id,
                tradesman_id=tradesman_id,
                title=title,
                description=description,
                date_started=date_started,
                date_finished=date_finished,
                call_out_fee=call_out_fee,
                materials_fee=materials_fee,
                hourly_rate=hourly_rate,
                hours_worked=hours_worked,
                daily_rate=daily_rate,
                days_worked=days_worked,
                total_cost=total_cost,
                rating=rating
            )
            flash("Job added successfully!", "success")
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")

        return redirect(url_for("tradesmen.view_tradesman", tradesman_id=tradesman_id))

    return render_template("add_job.html", tradesman_id=tradesman_id, tradesman=tradesman)

@jobs_bp.route("/add_quote/<int:tradesman_id>", methods=["GET", "POST"])
@login_required
def add_quote(tradesman_id):
    # Get tradesman information
    tradesman = tradesman_service.get_tradesman_by_id(tradesman_id)
    
    if not tradesman:
        flash("Tradesman not found.", "error")
        return redirect(url_for("search.search_tradesmen"))

    if request.method == "POST":
        user_id = session["user_id"]
        date_requested = request.form.get("date_requested")
        date_received = request.form.get("date_received")
        title = request.form.get("title")
        description = request.form.get("description")
        call_out_fee = request.form.get("call_out_fee")
        materials_fee = request.form.get("materials_fee")
        hourly_rate = request.form.get("hourly_rate")
        hours_estimated = request.form.get("hours_estimated")
        daily_rate = request.form.get("daily_rate")
        days_estimated = request.form.get("days_estimated")
        total_quote = request.form.get("total_quote")
        status = request.form.get("status", "pending")

        try:
            # Convert empty strings to None for optional fields
            call_out_fee = int(call_out_fee) if call_out_fee else None
            materials_fee = int(materials_fee) if materials_fee else None
            hourly_rate = int(hourly_rate) if hourly_rate else None
            hours_estimated = float(hours_estimated) if hours_estimated else None
            daily_rate = int(daily_rate) if daily_rate else None
            days_estimated = float(days_estimated) if days_estimated else None
            total_quote = int(total_quote) if total_quote else None
            
            job_service.create_quote(
                user_id=user_id,
                tradesman_id=tradesman_id,
                title=title,
                description=description,
                date_requested=date_requested,
                date_received=date_received,
                call_out_fee=call_out_fee,
                materials_fee=materials_fee,
                hourly_rate=hourly_rate,
                hours_estimated=hours_estimated,
                daily_rate=daily_rate,
                days_estimated=days_estimated,
                total_quote=total_quote
            )
            flash("Quote added successfully!", "success")
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")

        return redirect(url_for("tradesmen.view_tradesman", tradesman_id=tradesman_id))

    return render_template("add_quote.html", tradesman_id=tradesman_id, tradesman=tradesman)

@jobs_bp.route("/convert_quote_to_job/<int:quote_id>", methods=["POST"])
@login_required
def convert_quote_to_job(quote_id):
    """Convert a quote to a job when accepted"""
    try:
        quote = job_service.get_job_by_id(quote_id)
        if not quote or quote['type'] != 'quote':
            flash("Quote not found.", "error")
            return redirect(url_for("search.search_tradesmen"))
        
        if job_service.convert_quote_to_job(quote_id):
            flash("Quote converted to job successfully!", "success")
        else:
            flash("Failed to convert quote to job.", "error")
        
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
    
    return redirect(url_for("tradesmen.view_tradesman", tradesman_id=quote['tradesman_id']))

@jobs_bp.route("/reject_quote/<int:quote_id>", methods=["POST"])
@login_required
def reject_quote(quote_id):
    """Reject a quote"""
    try:
        quote = job_service.get_job_by_id(quote_id)
        if not quote or quote['type'] != 'quote':
            flash("Quote not found.", "error")
            return redirect(url_for("search.search_tradesmen"))
        
        if job_service.reject_quote(quote_id):
            flash("Quote declined successfully!", "success")
        else:
            flash("Failed to decline quote.", "error")
        
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
    
    return redirect(url_for("tradesmen.view_tradesman", tradesman_id=quote['tradesman_id']))

@jobs_bp.route('/view_quote/<int:quote_id>')
@login_required
def view_quote(quote_id):
    quote = job_service.get_job_by_id(quote_id)
    if not quote or quote['type'] != 'quote':
        flash("Quote not found.", "error")
        return redirect(url_for("search.search_tradesmen"))
    
    return render_template("view_quote.html", quote=quote)

@jobs_bp.route('/view_job/<int:job_id>')
@login_required
def view_job(job_id):
    job = job_service.get_job_by_id(job_id)
    if not job or job['type'] != 'job':
        flash("Job not found.", "error")
        return redirect(url_for("search.search_jobs"))
    
    return render_template("view_job.html", job=job)

@jobs_bp.route('/edit_job/<int:job_id>', methods=['GET', 'POST'])
@login_required
def edit_job(job_id):
    job = job_service.get_job_by_id(job_id)
    if not job or job['type'] != 'job':
        flash("Job not found.", "error")
        return redirect(url_for("search.search_jobs"))
    
    if not job_service.can_user_edit_job(session["user_id"], job_id):
        flash("You don't have permission to edit this job.", "error")
        return redirect(url_for("jobs.view_job", job_id=job_id))

    if request.method == "POST":
        date_started = request.form.get("date_started")
        date_finished = request.form.get("date_finished")
        title = request.form.get("title")
        description = request.form.get("description")
        call_out_fee = request.form.get("call_out_fee")
        materials_fee = request.form.get("materials_fee")
        hourly_rate = request.form.get("hourly_rate")
        hours_worked = request.form.get("hours_worked")
        daily_rate = request.form.get("daily_rate")
        days_worked = request.form.get("days_worked")
        total_cost = request.form.get("total_cost")
        rating = request.form.get("rating")

        try:
            # Convert empty strings to None for optional fields
            call_out_fee = int(call_out_fee) if call_out_fee else None
            materials_fee = int(materials_fee) if materials_fee else None
            hourly_rate = int(hourly_rate) if hourly_rate else None
            hours_worked = float(hours_worked) if hours_worked else None
            daily_rate = int(daily_rate) if daily_rate else None
            days_worked = float(days_worked) if days_worked else None
            total_cost = int(total_cost) if total_cost else None
            rating = int(rating) if rating else None
            
            job_service.update_job(
                job_id,
                title=title,
                description=description,
                date_started=date_started,
                date_finished=date_finished,
                call_out_fee=call_out_fee,
                materials_fee=materials_fee,
                hourly_rate=hourly_rate,
                hours_worked=hours_worked,
                daily_rate=daily_rate,
                days_worked=days_worked,
                total_cost=total_cost,
                rating=rating
            )
            flash("Job updated successfully!", "success")
            return redirect(url_for("jobs.view_job", job_id=job_id))
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")
            return redirect(url_for("jobs.edit_job", job_id=job_id))

    return render_template("edit_job.html", job=job)

# Legacy get_db function for backward compatibility
def get_db():
    from app.services.database import get_db_service
    return get_db_service().get_connection() 