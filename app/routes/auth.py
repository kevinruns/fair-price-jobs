from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from datetime import datetime, timedelta
from functools import wraps

from helpers import apology, login_required
from app.services.user_service import UserService

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

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            apology("must provide username", 403)
            return render_template("login.html"), 403

        # Ensure password was submitted
        elif not request.form.get("password"):
            apology("must provide password", 403)
            return render_template("login.html"), 403

        # Query database for username and verify password
        username = request.form.get("username")
        password = request.form.get("password")
        
        if not user_service.verify_password(username, password):
            apology("invalid username and/or password", 403)
            return render_template("login.html"), 403

        # Get user and remember which user has logged in
        user = user_service.get_user_by_username(username)
        session["user_id"] = user["id"]
        session["username"] = user["username"]  # Store username in session

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
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
        username = request.form.get("username")
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        email = request.form.get("email")
        postcode = request.form.get("postcode")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Input validation
        errors = []
        
        # Username validation
        if not username:
            errors.append("Must provide username")
        elif len(username) < 3:
            errors.append("Username must be at least 3 characters long")
        elif not username.isalnum():
            errors.append("Username must contain only letters and numbers")

        # Name validation
        if not firstname:
            errors.append("Must provide first name")
        elif not firstname.replace(" ", "").isalpha():
            errors.append("First name must contain only letters")
            
        if not lastname:
            errors.append("Must provide last name")
        elif not lastname.replace(" ", "").isalpha():
            errors.append("Last name must contain only letters")

        # Email validation
        if not email:
            errors.append("Must provide email address")
        elif not "@" in email or not "." in email:
            errors.append("Invalid email format")

        # Postcode validation (basic format check)
        if not postcode:
            errors.append("Must provide postcode")
        elif not postcode.replace(" ", "").isalnum():
            errors.append("Postcode must contain only letters and numbers")

        # Password validation
        if not password:
            errors.append("Must provide password")

        if not confirmation:
            errors.append("Must confirm password")
        elif password != confirmation:
            errors.append("Passwords do not match")

        if errors:
            for error in errors:
                flash(error, "error")
            return render_template("register.html")

        # Create new user
        try:
            user_id = user_service.create_user(username, firstname, lastname, email, postcode, password)
            flash("Registration successful.", "success")
            return redirect(url_for("auth.welcome", username=username))
        except Exception as e:
            flash("Username or email already taken", "error")
            return render_template("register.html")

    return render_template("register.html")

@auth_bp.route("/welcome/<username>")
def welcome(username):
    """Display welcome page after registration"""
    return render_template("welcome.html", username=username)

# Legacy get_db function for backward compatibility
def get_db():
    from app.services.database import get_db_service
    return get_db_service().get_connection() 