from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.wrappers.response import Response
from typing import Optional, List, Dict, Any, Union
from helpers import login_required
from app.services.group_service import GroupService

# Create Blueprint
groups_bp = Blueprint('groups', __name__)

# Initialize service
group_service = GroupService()

@groups_bp.route('/create_group', methods=['GET', 'POST'])
@login_required
def create_group() -> Union[str, Response]:
    if request.method == "POST":
        name: str = request.form.get('group_name', '')
        postcode: str = request.form.get('group_postcode', '')
        description: str = request.form.get('group_description', '').strip() or None
        try:
            group_id: int = group_service.create_group(name, postcode, description)
            group_service.add_user_to_group(session['user_id'], group_id, status='creator')
            
            flash('Group created successfully!', 'success')
            
            return redirect(url_for('groups.view_group', group_id=group_id))
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'error')
            return redirect(url_for('groups.create_group'))
    return render_template('create_group.html')

@groups_bp.route('/view_group/<int:group_id>', methods=['GET', 'POST'])
@login_required
def view_group(group_id: int) -> Union[str, Response]:
    group: Optional[Dict[str, Any]] = group_service.get_group_by_id(group_id)
    if not group:
        flash('Group not found.', 'error')
        return redirect(url_for('groups.search_groups'))
    members: List[Dict[str, Any]] = group_service.get_group_members(group_id)
    membership: Optional[Dict[str, Any]] = group_service.get_user_group_membership(session['user_id'], group_id)
    is_member: bool = bool(membership and membership['status'] in ['member', 'admin', 'creator'])
    is_admin_or_creator: bool = bool(membership and membership['status'] in ['admin', 'creator'])
    pending_requests_count: int = len(group_service.get_pending_requests(group_id))
    
    # Fetch tradesmen for this group
    from app.services.tradesman_service import TradesmanService
    tradesman_service = TradesmanService()
    tradesmen: List[Dict[str, Any]] = tradesman_service.get_tradesmen_by_group(group_id)
    
    # Fetch group creator information
    creator: Optional[Dict[str, Any]] = group_service.get_group_creator(group_id)
    
    # Fetch counts
    member_count: int = len(members) if members else 0
    tradesmen_count: int = len(tradesmen) if tradesmen else 0
    job_count: int = group_service.get_group_job_count(group_id)

    # Fetch pending requests if admin or creator
    pending_requests: List[Dict[str, Any]] = []
    if is_admin_or_creator:
        pending_requests = group_service.get_pending_requests(group_id)

    # Check if current user has a pending request
    pending_request: bool = bool(membership and membership['status'] == 'pending')

    if request.method == 'POST' and not is_member:
        try:
            # Check if user already has a request
            if membership and membership['status'] == 'pending':
                flash('You already have a pending request for this group.', 'warning')
            else:
                success = group_service.add_user_to_group(session['user_id'], group_id)
                if success:
                    tradesmen_added: int = group_service.add_user_tradesmen_to_group(session['user_id'], group_id)
                    if tradesmen_added > 0:
                        flash(f'Join request sent. {tradesmen_added} of your tradesmen have been automatically added to the group.', 'success')
                    else:
                        flash('Join request sent.', 'success')
                else:
                    flash('You already have a request for this group.', 'warning')
            return redirect(url_for('groups.view_group', group_id=group_id))
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'error')
    return render_template('view_group.html', group=group, members=members, tradesmen=tradesmen, creator=creator, member_count=member_count, tradesmen_count=tradesmen_count, job_count=job_count, is_member=is_member, is_admin_or_creator=is_admin_or_creator, pending_requests_count=pending_requests_count, pending_requests=pending_requests, pending_request=pending_request)

@groups_bp.route('/search_groups', methods=['GET', 'POST'])
@login_required
def search_groups() -> str:
    groups: List[Dict[str, Any]] = []
    if request.method == 'POST':
        name: Optional[str] = request.form.get('name')
        postcode: Optional[str] = request.form.get('postcode')
        groups = group_service.search_groups(name=name, postcode=postcode)
    else:
        groups = group_service.get_all_groups()
    
    # Add member count and user status to each group
    for group in groups:
        group['member_count'] = group_service.get_group_member_count(group['id'])
        # Check if current user is a member
        membership = group_service.get_user_group_membership(session['user_id'], group['id'])
        group['status'] = membership['status'] if membership else None
    
    return render_template('search_groups.html', groups=groups)

@groups_bp.route('/group_members/<int:group_id>')
@login_required
def group_members(group_id: int) -> Union[str, Response]:
    group: Optional[Dict[str, Any]] = group_service.get_group_by_id(group_id)
    if not group:
        flash('Group not found.', 'error')
        return redirect(url_for('groups.search_groups'))
    
    members: List[Dict[str, Any]] = group_service.get_group_members(group_id)
    return render_template('group_members.html', group_id=group_id, group_name=group['name'], members=members)

@groups_bp.route('/view_requests/<int:group_id>')
@login_required
def view_requests(group_id: int) -> str:
    pending_requests: List[Dict[str, Any]] = group_service.get_pending_requests(group_id)
    return render_template('view_all_pending_requests.html', requests=pending_requests)

@groups_bp.route('/view_all_pending_requests')
@login_required
def view_all_pending_requests() -> str:
    """Show all pending requests for groups where user is admin/creator"""
    requests: List[Dict[str, Any]] = group_service.get_all_pending_requests_for_user(session['user_id'])
    # Get all group memberships for the current user
    user_groups = group_service.get_user_groups(session['user_id'])
    admin_or_creator_group_ids = {g['id'] for g in user_groups if g['status'] in ['admin', 'creator']}
    return render_template('view_all_pending_requests.html', requests=requests, admin_or_creator_group_ids=admin_or_creator_group_ids)

@groups_bp.route('/handle_request/<int:request_id>/<action>', methods=['POST'])
@login_required
def handle_request(request_id: int, action: str) -> Response:
    try:
        # Get the request details
        request_data: Optional[Dict[str, Any]] = group_service.get_request_by_id(request_id)
        if not request_data:
            flash('Request not found.', 'error')
            return redirect(request.referrer or url_for('main.index'))
        
        group_id: int = request_data['group_id']
        user_id: int = request_data['user_id']
        
        # Check if current user has permission to handle requests (creator or admin)
        current_user_membership: Optional[Dict[str, Any]] = group_service.get_user_group_membership(session['user_id'], group_id)
        if not current_user_membership or current_user_membership['status'] not in ['creator', 'admin']:
            flash('You do not have permission to handle join requests.', 'error')
            return redirect(request.referrer or url_for('main.index'))
        
        if action == 'accept':
            # Update user status to 'member'
            group_service.update_user_group_status(user_id, group_id, 'member')
            
            # Automatically add all user's tradesmen to the group when their request is accepted
            tradesmen_added: int = group_service.add_user_tradesmen_to_group(user_id, group_id)
            
            if tradesmen_added > 0:
                flash(f'Request accepted. {tradesmen_added} tradesmen have been automatically added to the group.', 'success')
            else:
                flash('Request accepted.', 'success')
                
        elif action == 'reject':
            # Remove the request
            group_service.remove_user_from_group(user_id, group_id)
            flash('Request rejected.', 'info')
            
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
    
    return redirect(request.referrer or url_for('main.index'))

 