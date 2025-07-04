from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from helpers import login_required
from app.services.group_service import GroupService

# Create Blueprint
groups_bp = Blueprint('groups', __name__)

# Initialize service
group_service = GroupService()

@groups_bp.route('/create_group', methods=['GET', 'POST'])
@login_required
def create_group():
    if request.method == 'POST':
        name = request.form.get('group_name')
        postcode = request.form.get('group_postcode')
        try:
            group_id = group_service.create_group(name, postcode)
            group_service.add_user_to_group(session['user_id'], group_id, status='creator')
            
            # Automatically add all user's tradesmen to the group
            tradesmen_added = group_service.add_user_tradesmen_to_group(session['user_id'], group_id)
            
            if tradesmen_added > 0:
                flash(f'Group created successfully! {tradesmen_added} of your tradesmen have been automatically added to the group.', 'success')
            else:
                flash('Group created successfully!', 'success')
            
            return redirect(url_for('groups.view_group', group_id=group_id))
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'error')
            return redirect(url_for('groups.create_group'))
    return render_template('create_group.html')

@groups_bp.route('/view_group/<int:group_id>', methods=['GET', 'POST'])
@login_required
def view_group(group_id):
    group = group_service.get_group_by_id(group_id)
    if not group:
        flash('Group not found.', 'error')
        return redirect(url_for('groups.search_groups'))
    members = group_service.get_group_members(group_id)
    membership = group_service.get_user_group_membership(session['user_id'], group_id)
    is_member = membership and membership['status'] in ['member', 'admin', 'creator']
    is_admin_or_creator = membership and membership['status'] in ['admin', 'creator']
    pending_requests_count = len(group_service.get_pending_requests(group_id))
    
    # Fetch tradesmen for this group
    from app.services.tradesman_service import TradesmanService
    tradesman_service = TradesmanService()
    tradesmen = tradesman_service.get_tradesmen_by_group(group_id)
    
    # Fetch group creator information
    creator = group_service.get_group_creator(group_id)
    
    # Fetch counts
    member_count = len(members) if members else 0
    tradesmen_count = len(tradesmen) if tradesmen else 0
    job_count = group_service.get_group_job_count(group_id)
    
    if request.method == 'POST' and not is_member:
        try:
            group_service.add_user_to_group(session['user_id'], group_id)
            
            # Automatically add all user's tradesmen to the group when they join
            tradesmen_added = group_service.add_user_tradesmen_to_group(session['user_id'], group_id)
            
            if tradesmen_added > 0:
                flash(f'Join request sent. {tradesmen_added} of your tradesmen have been automatically added to the group.', 'success')
            else:
                flash('Join request sent.', 'success')
            
            return redirect(url_for('groups.view_group', group_id=group_id))
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'error')
    return render_template('view_group.html', group=group, members=members, tradesmen=tradesmen, creator=creator, member_count=member_count, tradesmen_count=tradesmen_count, job_count=job_count, is_member=is_member, is_admin_or_creator=is_admin_or_creator, pending_requests_count=pending_requests_count)

@groups_bp.route('/search_groups', methods=['GET', 'POST'])
@login_required
def search_groups():
    groups = []
    if request.method == 'POST':
        name = request.form.get('name')
        postcode = request.form.get('postcode')
        groups = group_service.search_groups(name=name, postcode=postcode)
    else:
        groups = group_service.get_all_groups()
    return render_template('search_groups.html', groups=groups)

@groups_bp.route('/group_members/<int:group_id>')
@login_required
def group_members(group_id):
    group = group_service.get_group_by_id(group_id)
    if not group:
        flash('Group not found.', 'error')
        return redirect(url_for('groups.search_groups'))
    
    members = group_service.get_group_members(group_id)
    return render_template('group_members.html', group_id=group_id, group_name=group['name'], members=members)

@groups_bp.route('/view_requests/<int:group_id>')
@login_required
def view_requests(group_id):
    pending_requests = group_service.get_pending_requests(group_id)
    return render_template('view_all_pending_requests.html', requests=pending_requests)

@groups_bp.route('/handle_request/<int:request_id>/<action>', methods=['POST'])
@login_required
def handle_request(request_id, action):
    try:
        if action == 'accept':
            # Get the request details
            request_data = group_service.get_request_by_id(request_id)
            if not request_data:
                flash('Request not found.', 'error')
                return redirect(request.referrer or url_for('main.index'))
            
            user_id = request_data['user_id']
            group_id = request_data['group_id']
            
            # Update user status to 'member'
            group_service.update_user_group_status(user_id, group_id, 'member')
            
            # Automatically add all user's tradesmen to the group when their request is accepted
            tradesmen_added = group_service.add_user_tradesmen_to_group(user_id, group_id)
            
            if tradesmen_added > 0:
                flash(f'Request accepted. {tradesmen_added} tradesmen have been automatically added to the group.', 'success')
            else:
                flash('Request accepted.', 'success')
                
        elif action == 'reject':
            # Remove the request
            group_service.remove_user_from_group(request_data['user_id'], request_data['group_id'])
            flash('Request rejected.', 'info')
            
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
    
    return redirect(request.referrer or url_for('main.index'))

# Legacy get_db function for backward compatibility
def get_db():
    from app.services.database import get_db_service
    return get_db_service().get_connection() 