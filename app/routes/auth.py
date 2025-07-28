from flask import Blueprint, flash, redirect, render_template, request, session, url_for, make_response
from werkzeug.wrappers.response import Response
from datetime import datetime, timedelta
from functools import wraps
from typing import Callable, Any, Dict, Optional, Union
from typing import cast

from app.helpers import login_required
from app.services.user_service import UserService
from app.validators import validate_form, StringValidator, EmailValidator, PasswordValidator
from app.exceptions import AuthenticationError, ValidationError, DuplicateResourceError

# Create Blueprint
auth_bp = Blueprint('auth', __name__)

# Initialize services
user_service = UserService()

# Rate limiting storage (persists across requests)
_rate_limit_attempts: Dict[str, list] = {}

# Rate limiting decorator
def rate_limit(limit: int = 5, window: int = 300) -> Callable:  # 5 attempts per 5 minutes
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapped(*args: Any, **kwargs: Any) -> Union[str, tuple[str, int], Response]:
            now = datetime.now()
            ip = request.remote_addr or "unknown"
            
            # Clean old attempts
            _rate_limit_attempts[ip] = [t for t in _rate_limit_attempts.get(ip, []) if now - t < timedelta(seconds=window)]
            
            if len(_rate_limit_attempts.get(ip, [])) >= limit:
                flash("Too many login attempts. Please try again later.", "error")
                return render_template("login.html"), 429
            
            # Call the original function
            result = f(*args, **kwargs)
            
            # Only count failed attempts (when login fails)
            # Check if this was a POST request and login failed
            if request.method == "POST":
                # If the result is a redirect to "/", login was successful
                # If the result is a rendered template, login failed
                if isinstance(result, Response) and result.status_code == 302 and result.location == "/":
                    # Successful login - don't count this attempt
                    pass
                else:
                    # Failed login - count this attempt
                    _rate_limit_attempts[ip] = _rate_limit_attempts.get(ip, []) + [now]
            
            if isinstance(result, (str, tuple, Response)):
                return result
            raise RuntimeError("rate_limit wrapped function did not return str, tuple[str, int], or Response")
        return wrapped
    return decorator

@auth_bp.route("/login", methods=["GET", "POST"])
@rate_limit() # Apply rate limiting to the login route
def login() -> Response:
    """Log user in"""
    # Forget any user_id
    session.clear()

    if request.method == "POST":
        # Validate input
        validators = {
            'username': StringValidator('username', min_length=1, required=True),
            'password': PasswordValidator('password', required=True)
        }
        
        try:
            # Validate form data
            validated_data: Dict[str, str] = {}
            for field_name, validator in validators.items():
                value = request.form.get(field_name)
                validated_data[field_name] = validator.validate(value)
            
            # Attempt login
            user = user_service.authenticate_user(
                validated_data['username'], 
                validated_data['password']
            )
            
            if user:
                # Remember which user has logged in
                session["user_id"] = user['id']
                session["username"] = user['username']
                
                # Check if there's a pending invitation to handle
                pending_invitation = session.get('pending_invitation')
                if pending_invitation:
                    # Clear the pending invitation from session
                    session.pop('pending_invitation', None)
                    
                    # Try to accept the invitation
                    from app.services.invitation_service import InvitationService
                    invitation_service = InvitationService()
                    invitation = invitation_service.get_invitation_by_token(pending_invitation)
                    
                    if invitation:
                        success = invitation_service.accept_invitation(pending_invitation, user['id'])
                        if success:
                            flash(f'Welcome to {invitation["group_name"]}!', 'success')
                            return redirect(url_for('groups.view_group', group_id=invitation['group_id']))
                        else:
                            flash('Failed to accept invitation. You may already be a member of this group.', 'error')
                    else:
                        flash('Invalid or expired invitation.', 'error')
                
                # Redirect user to home page
                return redirect("/")
            else:
                flash("Invalid username and/or password", "error")
                return make_response(render_template("login.html"))
                
        except ValidationError as e:
            flash(e.message, "error")
            return make_response(render_template("login.html"))
        except AuthenticationError as e:
            flash(e.message, "error")
            return make_response(render_template("login.html"))

    # User reached route via GET (as by clicking a link or via redirect)
    return make_response(render_template("login.html"))

@auth_bp.route("/logout")
def logout() -> Response:
    """Log user out"""
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")

@auth_bp.route("/register", methods=["GET", "POST"])
def register() -> Response:
    # Get invitation token from query parameter or session
    invitation_token = request.args.get('invitation_token') or session.get('pending_invitation')
    invitation_info = None
    
    # If there's an invitation token, get the invitation details
    if invitation_token:
        from app.services.invitation_service import InvitationService
        invitation_service = InvitationService()
        invitation_info = invitation_service.get_invitation_by_token(invitation_token)
        
        # If invitation is invalid, clear it and show normal registration
        if not invitation_info:
            session.pop('pending_invitation', None)
            invitation_token = None
            invitation_info = None
    
    if request.method == "POST":
        # Define validators for registration
        validators = {
            'username': StringValidator('username', min_length=3, pattern=r'^[a-zA-Z0-9_]+$', required=True),
            'firstname': StringValidator('firstname', min_length=1, pattern=r'^[a-zA-Z\s]+$', required=True),
            'lastname': StringValidator('lastname', min_length=1, pattern=r'^[a-zA-Z\s]+$', required=True),
            'email': EmailValidator('email', required=True),
            'postcode': StringValidator('postcode', min_length=1, pattern=r'^[a-zA-Z0-9\s]+$', required=True),
            'password': PasswordValidator('password', min_length=6, required=True),
            'confirmation': StringValidator('confirmation', required=True)
        }
        
        try:
            # Validate form data
            validated_data: Dict[str, str] = {}
            for field_name, validator in validators.items():
                value = request.form.get(field_name)
                validated_data[field_name] = validator.validate(value)
            
            # Check password confirmation
            if validated_data['password'] != validated_data['confirmation']:
                raise ValidationError("Passwords do not match", "confirmation")
            
            # Create new user
            user_id = user_service.create_user(
                username=validated_data['username'],
                firstname=validated_data['firstname'],
                lastname=validated_data['lastname'],
                email=validated_data['email'],
                postcode=validated_data['postcode'],
                password=validated_data['password']
            )
            
            # Check for and accept any pending invitations for this email
            from app.services.invitation_service import InvitationService
            invitation_service = InvitationService()
            accepted_groups = invitation_service.accept_all_pending_invitations_for_user(
                user_id, validated_data['email']
            )
            
            if accepted_groups:
                group_names = [group['group_name'] for group in accepted_groups]
                flash(f"Registration successful! You have been automatically added to: {', '.join(group_names)}", "success")
            else:
                flash("Registration successful.", "success")
            
            return redirect(url_for("auth.welcome", username=validated_data['username']))
            
        except ValidationError as e:
            flash(e.message, "error")
            return make_response(render_template("register.html", invitation_info=invitation_info))
        except DuplicateResourceError as e:
            flash(e.message, "error")
            return make_response(render_template("register.html", invitation_info=invitation_info))
        except Exception as e:
            flash("An error occurred during registration. Please try again.", "error")
            return make_response(render_template("register.html", invitation_info=invitation_info))

    return make_response(render_template("register.html", invitation_info=invitation_info))

@auth_bp.route("/welcome/<username>")
def welcome(username: str) -> str:
    """Display welcome page after registration"""
    return render_template("welcome.html", username=username)

 