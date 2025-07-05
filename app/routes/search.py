from flask import Blueprint, render_template, request, session, flash, redirect, url_for, Response
from typing import Any, Dict, List, Optional, Union
from helpers import login_required
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
    tradesmen: List[Dict[str, Any]] = []
    if request.method == 'POST':
        search_term = request.form.get('search_term')
        trade = request.form.get('trade')
        postcode = request.form.get('postcode')
        tradesmen = tradesman_service.search_tradesmen(search_term, trade, postcode)
    return render_template('search_tradesmen.html', tradesmen=tradesmen)

@search_bp.route('/search_jobs', methods=['GET', 'POST'])
@login_required
def search_jobs() -> str:
    jobs: List[Dict[str, Any]] = []
    if request.method == 'POST':
        search_term = request.form.get('search_term')
        trade = request.form.get('trade')
        rating = request.form.get('rating')
        added_by_user = request.form.get('added_by_user')
        group = request.form.get('group')
        jobs = job_service.search_jobs(search_term, trade, rating, added_by_user, group)
    return render_template('search_jobs.html', jobs=jobs)

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

 