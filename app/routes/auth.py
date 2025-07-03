from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
import sqlite3
from functools import wraps

from helpers import apology, login_required

# Create Blueprint
auth_bp = Blueprint('auth', __name__)

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

        # Query database for username
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),))
        rows = cursor.fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            apology("invalid username and/or password", 403)
            return render_template("login.html"), 403

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]  # Store username in session

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

        # Hash the password
        hash = generate_password_hash(password)

        # Insert new user into database
        db = get_db()
        try:
            with db:
                db.execute("INSERT INTO users (username, firstname, lastname, email, postcode, hash) VALUES (?, ?, ?, ?, ?, ?)", 
                           (username, firstname, lastname, email, postcode, hash))
            flash("Registration successful.", "success")
            return redirect(url_for("auth.welcome", username=username))
        except sqlite3.IntegrityError:
            flash("Username or email already taken", "error")
            return render_template("register.html")
        except Exception as e:
            flash("An error occurred during registration. Please try again.", "error")
            return render_template("register.html")

    return render_template("register.html")

@auth_bp.route("/welcome/<username>")
def welcome(username):
    """Display welcome page after registration"""
    return render_template("welcome.html", username=username)

# Import get_db function - this will be moved to a database service later
def get_db():
    from flask import g
    db = getattr(g, '_database', None)
    if db is None:
        from app.config import DATABASE
        import sqlite3
        db = g._database = sqlite3.connect(DATABASE, isolation_level=None)
        db.row_factory = sqlite3.Row
    return db 