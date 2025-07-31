from flask import Blueprint, render_template, request, session, flash, redirect, url_for, Response
from typing import Any, Dict, List, Optional, Union
from app.helpers import login_required
from app.services.tradesman_service import TradesmanService
from app.services.job_service import JobService
from app.services.group_service import GroupService

# Create Blueprint
search_bp = Blueprint('search', __name__)

# Initialize services
tradesman_service = TradesmanService()
job_service = JobService()
group_service = GroupService()

@search_bp.route('/search_tradesmen', methods=['GET', 'POST'])
@login_required
def search_tradesmen() -> str:
    message = request.args.get('message')
    tradesmen: List[Dict[str, Any]] = []
    
    # Initialize form data variables
    search_term = ''
    selected_trade = ''
    postcode = ''
    selected_user = ''
    selected_group = ''
    
    if request.method == 'POST':
        search_term = request.form.get('search_term', '')
        trade = request.form.get('trade', '')
        postcode = request.form.get('postcode', '')
        added_by_user = request.form.get('added_by_user', '')
        group = request.form.get('group', '')
        
        # Update selected values for form persistence
        selected_trade = trade
        selected_user = added_by_user
        selected_group = group
        
        tradesmen = tradesman_service.search_tradesmen(search_term, trade, postcode)
    
    # Get filter options
    trades = tradesman_service.get_unique_trades()
    users = tradesman_service.get_unique_users()
    groups = tradesman_service.get_unique_groups()
    
    return render_template('search_tradesmen.html', 
                         tradesmen=tradesmen, 
                         message=message,
                         trades=trades,
                         users=users,
                         groups=groups,
                         search_term=search_term,
                         selected_trade=selected_trade,
                         postcode=postcode,
                         selected_user=selected_user,
                         selected_group=selected_group)

@search_bp.route('/search_jobs_quotes', methods=['GET', 'POST'])
@login_required
def search_jobs_quotes() -> str:
    jobs: List[Dict[str, Any]] = []
    quotes: List[Dict[str, Any]] = []
    combined_results: List[Dict[str, Any]] = []
    
    # Initialize form data variables
    search_term = ''
    selected_trade = ''
    selected_rating = ''
    selected_user = ''
    selected_group = ''
    include_jobs = 'on'
    include_quotes = 'on'
    
    if request.method == 'POST':
        search_term = request.form.get('search_term', '')
        trade = request.form.get('trade', '')
        rating = request.form.get('rating', '')
        added_by_user = request.form.get('added_by_user', '')
        group = request.form.get('group', '')
        include_jobs = request.form.get('include_jobs', 'on')
        include_quotes = request.form.get('include_quotes', 'on')
        
        # Update selected values for form persistence
        selected_trade = trade
        selected_rating = rating
        selected_user = added_by_user
        selected_group = group
        
        # Search for jobs if requested
        if include_jobs == 'on':
            jobs = job_service.search_jobs(search_term, trade, rating, added_by_user, group)
            for job in jobs:
                job['type'] = 'job'
                combined_results.append(job)
        
        # Search for quotes if requested
        if include_quotes == 'on':
            quotes = job_service.search_quotes(search_term, trade, None, None)
            for quote in quotes:
                quote['type'] = 'quote'
                combined_results.append(quote)
        
        # Sort combined results by date (most recent first)
        combined_results.sort(key=lambda x: x.get('date_finished') or x.get('date_requested') or '', reverse=True)
    
    # Get filter options
    trades = job_service.get_unique_trades()
    users = job_service.get_unique_users()
    groups = job_service.get_unique_groups()
    
    return render_template('search_jobs_quotes.html', 
                         results=combined_results, 
                         trades=trades, 
                         users=users, 
                         groups=groups,
                         search_term=search_term,
                         selected_trade=selected_trade,
                         selected_rating=selected_rating,
                         selected_user=selected_user,
                         selected_group=selected_group,
                         include_jobs=include_jobs,
                         include_quotes=include_quotes)

@search_bp.route('/search_groups', methods=['GET', 'POST'])
@login_required
def search_groups() -> str:
    groups: List[Dict[str, Any]] = []
    if request.method == 'POST':
        name = request.form.get('name')
        postcode = request.form.get('postcode')
        groups = group_service.search_groups(name=name, postcode=postcode)
    else:
        groups = group_service.get_all_groups()
    return render_template('search_groups.html', groups=groups)

 