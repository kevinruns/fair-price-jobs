from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from helpers import login_required
from app.services.tradesman_service import TradesmanService
from app.services.job_service import JobService

# Create Blueprint
search_bp = Blueprint('search', __name__)

# Initialize services
tradesman_service = TradesmanService()
job_service = JobService()

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
        
        # Search tradesmen using service
        tradesmen = tradesman_service.search_tradesmen(
            search_term=search_term,
            trade=trade,
            postcode=postcode
        )
        
        # Get unique trades for the filter dropdown
        trades = tradesman_service.get_unique_trades()
        
        return render_template("search_tradesmen.html", 
                             tradesmen=tradesmen,
                             trades=trades,
                             search_term=search_term,
                             selected_trade=trade,
                             postcode=postcode,
                             message=message)
    
    # GET request - show empty search form
    trades = tradesman_service.get_unique_trades()
    
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
        
        # Search jobs using service
        jobs = job_service.search_jobs(
            search_term=search_term,
            trade=trade,
            rating=rating,
            added_by_user=added_by_user,
            group=group
        )
        
        # Get filter options
        trades = job_service.get_unique_trades()
        users = job_service.get_unique_users()
        groups = job_service.get_unique_groups()
        
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
    trades = job_service.get_unique_trades()
    users = job_service.get_unique_users()
    groups = job_service.get_unique_groups()
    
    return render_template("search_jobs.html", 
                         trades=trades,
                         users=users,
                         groups=groups)

 