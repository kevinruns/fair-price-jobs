from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.wrappers.response import Response
from typing import Optional, List, Dict, Any, Union
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
def add_job(tradesman_id: int) -> Union[str, Response]:
    # Get tradesman information
    tradesman = tradesman_service.get_tradesman_by_id(tradesman_id)
    
    if not tradesman:
        flash("Tradesman not found.", "error")
        return redirect(url_for("search.search_tradesmen"))

    if request.method == "POST":
        user_id = session["user_id"]
        date_started = request.form.get("date_started") or None
        date_finished = request.form.get("date_finished") or None
        title = request.form.get("title") or ""
        description = request.form.get("description") or ""
        call_out_fee = request.form.get("call_out_fee")
        materials_fee = request.form.get("materials_fee")
        hourly_rate = request.form.get("hourly_rate")
        hours_worked = request.form.get("hours_worked")
        daily_rate = request.form.get("daily_rate")
        days_worked = request.form.get("days_worked")
        total_cost = request.form.get("total_cost")
        rating = request.form.get("rating")

        try:
            # Convert empty strings to None for optional fields and cast to correct types
            call_out_fee_int = int(call_out_fee) if call_out_fee else None
            materials_fee_int = int(materials_fee) if materials_fee else None
            hourly_rate_int = int(hourly_rate) if hourly_rate else None
            hours_worked_float = float(hours_worked) if hours_worked else None
            daily_rate_int = int(daily_rate) if daily_rate else None
            days_worked_float = float(days_worked) if days_worked else None
            total_cost_int = int(total_cost) if total_cost else None
            rating_int = int(rating) if rating else None
            
            job_service.create_job(
                user_id=user_id,
                tradesman_id=tradesman_id,
                title=title,
                description=description,
                date_started=date_started,
                date_finished=date_finished,
                call_out_fee=call_out_fee_int,
                materials_fee=materials_fee_int,
                hourly_rate=hourly_rate_int,
                hours_worked=hours_worked_float,
                daily_rate=daily_rate_int,
                days_worked=days_worked_float,
                total_cost=total_cost_int,
                rating=rating_int
            )
            flash("Job added successfully!", "success")
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")

        return redirect(url_for("tradesmen.view_tradesman", tradesman_id=tradesman_id))

    return render_template("add_job.html", tradesman_id=tradesman_id, tradesman=tradesman)

@jobs_bp.route("/add_quote/<int:tradesman_id>", methods=["GET", "POST"])
@login_required
def add_quote(tradesman_id: int) -> Union[str, Response]:
    # Get tradesman information
    tradesman = tradesman_service.get_tradesman_by_id(tradesman_id)
    
    if not tradesman:
        flash("Tradesman not found.", "error")
        return redirect(url_for("search.search_tradesmen"))

    if request.method == "POST":
        user_id = session["user_id"]
        date_requested = request.form.get("date_requested") or None
        date_received = request.form.get("date_received") or None
        title = request.form.get("title") or ""
        description = request.form.get("description") or ""
        call_out_fee = request.form.get("call_out_fee")
        materials_fee = request.form.get("materials_fee")
        hourly_rate = request.form.get("hourly_rate")
        hours_estimated = request.form.get("hours_estimated")
        daily_rate = request.form.get("daily_rate")
        days_estimated = request.form.get("days_estimated")
        total_quote = request.form.get("total_quote")
        status = request.form.get("status", "pending")

        try:
            # Convert empty strings to None for optional fields and cast to correct types
            call_out_fee_int = int(call_out_fee) if call_out_fee else None
            materials_fee_int = int(materials_fee) if materials_fee else None
            hourly_rate_int = int(hourly_rate) if hourly_rate else None
            hours_estimated_float = float(hours_estimated) if hours_estimated else None
            daily_rate_int = int(daily_rate) if daily_rate else None
            days_estimated_float = float(days_estimated) if days_estimated else None
            total_quote_int = int(total_quote) if total_quote else None
            
            job_service.create_quote(
                user_id=user_id,
                tradesman_id=tradesman_id,
                title=title,
                description=description,
                date_requested=date_requested,
                date_received=date_received,
                call_out_fee=call_out_fee_int,
                materials_fee=materials_fee_int,
                hourly_rate=hourly_rate_int,
                hours_estimated=hours_estimated_float,
                daily_rate=daily_rate_int,
                days_estimated=days_estimated_float,
                total_quote=total_quote_int
            )
            flash("Quote added successfully!", "success")
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")

        return redirect(url_for("tradesmen.view_tradesman", tradesman_id=tradesman_id))

    return render_template("add_quote.html", tradesman_id=tradesman_id, tradesman=tradesman)

@jobs_bp.route("/convert_quote_to_job/<int:quote_id>", methods=["POST"])
@login_required
def convert_quote_to_job(quote_id: int) -> Union[str, Response]:
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
    
    if quote and 'tradesman_id' in quote:
        return redirect(url_for("tradesmen.view_tradesman", tradesman_id=quote['tradesman_id']))
    else:
        return redirect(url_for("search.search_tradesmen"))

@jobs_bp.route("/reject_quote/<int:quote_id>", methods=["POST"])
@login_required
def reject_quote(quote_id: int) -> Union[str, Response]:
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
    
    if quote and 'tradesman_id' in quote:
        return redirect(url_for("tradesmen.view_tradesman", tradesman_id=quote['tradesman_id']))
    else:
        return redirect(url_for("search.search_tradesmen"))

@jobs_bp.route('/view_quote/<int:quote_id>')
@login_required
def view_quote(quote_id: int) -> Union[str, Response]:
    quote = job_service.get_job_by_id(quote_id)
    if not quote or quote['type'] != 'quote':
        flash("Quote not found.", "error")
        return redirect(url_for("search.search_tradesmen"))
    
    return render_template("view_quote.html", quote=quote)

@jobs_bp.route('/view_job/<int:job_id>')
@login_required
def view_job(job_id: int) -> Union[str, Response]:
    job = job_service.get_job_by_id(job_id)
    if not job or job['type'] != 'job':
        flash("Job not found.", "error")
        return redirect(url_for("search.search_jobs_quotes"))
    
    return render_template("view_job.html", job=job)

@jobs_bp.route('/edit_job/<int:job_id>', methods=['GET', 'POST'])
@login_required
def edit_job(job_id: int) -> Union[str, Response]:
    job = job_service.get_job_by_id(job_id)
    if not job or job['type'] != 'job':
        flash("Job not found.", "error")
        return redirect(url_for("search.search_jobs_quotes"))
    
    if not job_service.can_user_edit_job(session["user_id"], job_id):
        flash("You don't have permission to edit this job.", "error")
        return redirect(url_for("search.search_jobs_quotes"))

    if request.method == "POST":
        # Get form data
        title = request.form.get("title") or ""
        description = request.form.get("description") or ""
        date_started = request.form.get("date_started") or None
        date_finished = request.form.get("date_finished") or None
        call_out_fee = request.form.get("call_out_fee")
        materials_fee = request.form.get("materials_fee")
        hourly_rate = request.form.get("hourly_rate")
        hours_worked = request.form.get("hours_worked")
        daily_rate = request.form.get("daily_rate")
        days_worked = request.form.get("days_worked")
        total_cost = request.form.get("total_cost")
        rating = request.form.get("rating")

        try:
            call_out_fee_int = int(call_out_fee) if call_out_fee else None
            materials_fee_int = int(materials_fee) if materials_fee else None
            hourly_rate_int = int(hourly_rate) if hourly_rate else None
            hours_worked_float = float(hours_worked) if hours_worked else None
            daily_rate_int = int(daily_rate) if daily_rate else None
            days_worked_float = float(days_worked) if days_worked else None
            total_cost_int = int(total_cost) if total_cost else None
            rating_int = int(rating) if rating else None
            job_service.update_job(
                job_id,
                title=title,
                description=description,
                date_started=date_started,
                date_finished=date_finished,
                call_out_fee=call_out_fee_int,
                materials_fee=materials_fee_int,
                hourly_rate=hourly_rate_int,
                hours_worked=hours_worked_float,
                daily_rate=daily_rate_int,
                days_worked=days_worked_float,
                total_cost=total_cost_int,
                rating=rating_int
            )
            flash("Job updated successfully!", "success")
            return redirect(url_for("jobs.view_job", job_id=job_id))
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")
            return redirect(url_for("jobs.edit_job", job_id=job_id))

    return render_template("edit_job.html", job=job, can_delete=job_service.can_user_edit_job(session["user_id"], job_id))

@jobs_bp.route("/delete_job/<int:job_id>")
@login_required
def delete_job(job_id: int) -> Union[str, Response]:
    """Delete a job if the user has permission."""
    try:
        # Check if the job exists and belongs to the current user
        can_delete = job_service.can_user_edit_job(session["user_id"], job_id)
        job = job_service.get_job_by_id(job_id)
        
        if not job or not can_delete:
            flash("Job not found or you don't have permission to delete it.", "error")
            return redirect(url_for("search.search_jobs_quotes"))
        
        # Store tradesman_id for redirect
        tradesman_id = job.get('tradesman_id')
        
        # Delete the job
        if job_service.delete_job(job_id):
            flash("Job deleted successfully!", "success")
            # Redirect to tradesman view if we have the ID, otherwise to search
            if tradesman_id:
                return redirect(url_for("tradesmen.view_tradesman", tradesman_id=tradesman_id))
            else:
                return redirect(url_for("search.search_jobs_quotes"))
        else:
            flash("Failed to delete job.", "error")
            return redirect(url_for("jobs.edit_job", job_id=job_id))
            
    except Exception as e:
        flash(f"An error occurred while deleting the job: {str(e)}", "error")
        return redirect(url_for("jobs.edit_job", job_id=job_id))

 