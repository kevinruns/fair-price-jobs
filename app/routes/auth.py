from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from datetime import datetime, timedelta
from functools import wraps

from helpers import login_required
from app.services.user_service import UserService
from app.validators import validate_form, StringValidator, EmailValidator, PasswordValidator
from app.exceptions import AuthenticationError, ValidationError, DuplicateResourceError

# Create Blueprint
auth_bp = Blueprint('auth', __name__)

# Initialize services
user_service = UserService()

# Rate limiting decorator
def rate_limit(limit=5, window=300):  # 5 attempts per 5 minutes
    def decorator(f):
        attempts = {}
        @wraps(f)
        def wrapped(*args, **kwargs):
            now = datetime.now()
            ip = request.remote_addr
            
            # Clean old attempts
            attempts[ip] = [t for t in attempts.get(ip, []) if now - t < timedelta(seconds=window)]
            
            if len(attempts.get(ip, [])) >= limit:
                flash("Too many login attempts. Please try again later.", "error")
                return render_template("login.html"), 429
            
            attempts[ip] = attempts.get(ip, []) + [now]
            return f(*args, **kwargs)
        return wrapped
    return decorator

@auth_bp.route("/login", methods=["GET", "POST"])
@rate_limit()
def login():
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
            validated_data = {}
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
                
                # Redirect user to home page
                return redirect("/")
            else:
                flash("Invalid username and/or password", "error")
                return render_template("login.html")
                
        except ValidationError as e:
            flash(e.message, "error")
            return render_template("login.html")
        except AuthenticationError as e:
            flash(e.message, "error")
            return render_template("login.html")

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
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
            validated_data = {}
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
            
            flash("Registration successful.", "success")
            return redirect(url_for("auth.welcome", username=validated_data['username']))
            
        except ValidationError as e:
            flash(e.message, "error")
            return render_template("register.html")
        except DuplicateResourceError as e:
            flash(e.message, "error")
            return render_template("register.html")
        except Exception as e:
            flash("An error occurred during registration. Please try again.", "error")
            return render_template("register.html")

    return render_template("register.html")

@auth_bp.route("/welcome/<username>")
def welcome(username):
    """Display welcome page after registration"""
    return render_template("welcome.html", username=username)

 