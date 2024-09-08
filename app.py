# Configure application
from flask import Flask, g, flash, redirect, render_template, request, session, url_for
from flask_session import Session


from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import sqlite3
import os


from helpers import apology, login_required


app = Flask(__name__)


# Configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Database configuration
DATABASE = 'application.db'  # This is your database name


@app.route("/")
@login_required
def index():
    """Show index"""

    if (session["user_id"]):


        return render_template("index.html")
    

    


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),))
        rows = cursor.fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")





@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")




@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        email = request.form.get("email")
        postcode = request.form.get("postcode")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Validate form inputs
        if not username:
            flash("Must provide username", "error")
            return render_template("register.html")
        elif not firstname:
            flash("Must provide first name", "error")
            return render_template("register.html")
        elif not lastname:
            flash("Must provide last name", "error")
            return render_template("register.html")
        elif not email:
            flash("Must provide email address", "error")
            return render_template("register.html")
        elif not postcode:
            flash("Must provide postcode", "error")
            return render_template("register.html")
        elif not password:
            flash("Must provide password", "error")
            return render_template("register.html")
        elif not confirmation:
            flash("Must confirm password", "error")
            return render_template("register.html")
        elif password != confirmation:
            flash("Passwords do not match", "error")
            return render_template("register.html")

        # Hash the password
        hash = generate_password_hash(password)

        # Insert new user into database
        db = get_db()
        try:
            db.execute("INSERT INTO users (username, firstname, lastname, email, postcode, hash) VALUES (?, ?, ?, ?, ?, ?)", 
                       (username, firstname, lastname, email, postcode, hash))
            db.commit()
        except sqlite3.IntegrityError:
            flash("Username or email already taken", "error")
            return render_template("register.html")

        # Redirect user to welcome page
        flash("Registration successful.", "success")
        return redirect(url_for("welcome", username=username))

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("register.html")


@app.route("/welcome/<username>")
def welcome(username):
    """Display welcome page after registration"""
    return render_template("welcome.html", username=username)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.route('/init_db')
def initialize_db():
    init_db()
    return 'Database initialized.'



if __name__ == '__main__':
    app.run(debug=True)


