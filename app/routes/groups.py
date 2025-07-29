from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.wrappers.response import Response
from typing import Optional, List, Dict, Any, Union
from app.helpers import login_required
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
            # Use the new method that creates group and adds creator in a single transaction
            group_id: int = group_service.create_group_with_creator(name, postcode, session['user_id'], description)
            
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

@groups_bp.route('/send_invitation/<int:group_id>', methods=['GET', 'POST'])
@login_required
def send_invitation(group_id: int) -> Union[str, Response]:
    """Send an email invitation to join a group."""
    # Check if user has permission to send invitations (admin or creator)
    membership = group_service.get_user_group_membership(session['user_id'], group_id)
    if not membership or membership['status'] not in ['admin', 'creator']:
        flash('You do not have permission to send invitations for this group.', 'error')
        return redirect(url_for('groups.view_group', group_id=group_id))
    
    group = group_service.get_group_by_id(group_id)
    if not group:
        flash('Group not found.', 'error')
        return redirect(url_for('groups.search_groups'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        if not email:
            flash('Please enter a valid email address.', 'error')
            return redirect(url_for('groups.send_invitation', group_id=group_id))
        
        try:
            from app.services.invitation_service import InvitationService
            invitation_service = InvitationService()
            
            # Check if user with this email already exists and is in the group
            from app.services.user_service import UserService
            user_service = UserService()
            existing_user = user_service.get_user_by_email(email)
            
            if existing_user:
                existing_membership = group_service.get_user_group_membership(existing_user['id'], group_id)
                if existing_membership:
                    flash('A user with this email is already a member of this group.', 'warning')
                    return redirect(url_for('groups.send_invitation', group_id=group_id))
            
            # Check email configuration before attempting to send
            if not invitation_service.email_service.is_configured():
                flash('Email configuration is incomplete. Please contact the administrator to set up email invitations.', 'error')
                return redirect(url_for('groups.send_invitation', group_id=group_id))
            
            # Send invitation
            success = invitation_service.send_invitation_email(group_id, session['user_id'], email)
            
            if success:
                flash('Invitation sent successfully!', 'success')
            else:
                flash('Failed to send invitation. Please check your email configuration or try again later.', 'error')
                
        except Exception as e:
            flash(f'An error occurred while sending invitation: {str(e)}', 'error')
        
        return redirect(url_for('groups.view_group', group_id=group_id))
    
    return render_template('send_invitation.html', group=group)

@groups_bp.route('/view_invitations/<int:group_id>')
@login_required
def view_invitations(group_id: int) -> Union[str, Response]:
    """View all pending invitations for a group."""
    # Check if user has permission to view invitations (admin or creator)
    membership = group_service.get_user_group_membership(session['user_id'], group_id)
    if not membership or membership['status'] not in ['admin', 'creator']:
        flash('You do not have permission to view invitations for this group.', 'error')
        return redirect(url_for('groups.view_group', group_id=group_id))
    
    group = group_service.get_group_by_id(group_id)
    if not group:
        flash('Group not found.', 'error')
        return redirect(url_for('groups.search_groups'))
    
    from app.services.invitation_service import InvitationService
    invitation_service = InvitationService()
    invitations = invitation_service.get_pending_invitations_for_group(group_id)
    
    return render_template('view_invitations.html', group=group, invitations=invitations)

@groups_bp.route('/cancel_invitation/<int:invitation_id>', methods=['POST'])
@login_required
def cancel_invitation(invitation_id: int) -> Response:
    """Cancel a pending invitation."""
    try:
        from app.services.invitation_service import InvitationService
        invitation_service = InvitationService()
        
        success = invitation_service.cancel_invitation(invitation_id, session['user_id'])
        
        if success:
            flash('Invitation cancelled successfully.', 'success')
        else:
            flash('Failed to cancel invitation or you do not have permission.', 'error')
            
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
    
    return redirect(request.referrer or url_for('main.index'))

@groups_bp.route('/invitation/<token>')
def invitation(token: str) -> Union[str, Response]:
    """Handle invitation acceptance."""
    from app.services.invitation_service import InvitationService
    invitation_service = InvitationService()
    
    invitation = invitation_service.get_invitation_by_token(token)
    if not invitation:
        flash('Invalid or expired invitation.', 'error')
        return redirect(url_for('auth.register'))
    
    # If user is not logged in, redirect to registration with invitation token
    if 'user_id' not in session:
        # Store invitation token in session for after registration
        session['pending_invitation'] = token
        # Redirect to registration with invitation info
        return redirect(url_for('auth.register', invitation_token=token))
    
    # User is logged in, accept the invitation
    success = invitation_service.accept_invitation(token, session['user_id'])
    
    if success:
        flash(f'Welcome to {invitation["group_name"]}!', 'success')
        return redirect(url_for('groups.view_group', group_id=invitation['group_id']))
    else:
        flash('Failed to accept invitation. You may already be a member of this group.', 'error')
        return redirect(url_for('groups.search_groups'))

@groups_bp.route('/test_email_config')
@login_required
def test_email_config():
    """Test email configuration (for debugging)."""
    try:
        from app.services.email_service import EmailService
        email_service = EmailService()
        
        # Check OAuth configuration
        config_status = email_service.get_configuration_status()
        
        # Test connection
        connection_test = email_service.test_connection()
        
        return f"""
        <h2>Email Configuration Test</h2>
        <h3>OAuth Configuration:</h3>
        <ul>
            <li>OAuth Configured: {config_status['oauth_configured']}</li>
            <li>Client ID: {config_status['client_id']}</li>
            <li>Client Secret: {config_status['client_secret']}</li>
            <li>Refresh Token: {config_status['refresh_token']}</li>
            <li>From Email: {config_status['from_email']}</li>
            <li>App URL: {config_status['app_url']}</li>
            <li>Access Token Valid: {config_status['access_token_valid']}</li>
        </ul>
        <h3>Connection Test:</h3>
        <p>Connection {'SUCCESSFUL' if connection_test else 'FAILED'}</p>
        """
    except Exception as e:
        return f"Error testing email configuration: {str(e)}"

 