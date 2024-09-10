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

    if session.get("user_id"):
        db = get_db()
        cursor = db.cursor()
        
        # Fetch the username
        cursor.execute("SELECT username FROM users WHERE id = ?", (session["user_id"],))
        user = cursor.fetchone()
        username = user["username"] if user else "Unknown"
        
        # Fetch the groups the user is in
        cursor.execute("""
            SELECT g.id, g.name, g.postcode 
            FROM groups g
            JOIN user_groups ug ON g.id = ug.group_id
            WHERE ug.user_id = ?
        """, (session["user_id"],))
        groups = cursor.fetchall()
        
        return render_template("index.html", username=username, groups=groups)
    else:
        return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
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
        db = g._database = sqlite3.connect(DATABASE, isolation_level=None)
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



@app.route("/create_group", methods=["GET", "POST"])
@login_required
def create_group():
    print("Create group route accessed")
    if request.method == "POST":
        group_name = request.form.get("group_name")
        group_postcode = request.form.get("group_postcode")
        
        if not group_name or not group_postcode:
            flash("Please provide both group name and postcode", "error")
            return render_template("create_group.html")
        
        db = get_db()
        try:
            # Start a transaction
            with db:
                # Insert the new group
                cursor = db.execute("INSERT INTO groups (name, postcode) VALUES (?, ?)", 
                                    (group_name, group_postcode))
                group_id = cursor.lastrowid  # Get the ID of the newly created group
                
                # Add the current user to the group
                user_id = session.get("user_id")
                db.execute("INSERT INTO user_groups (user_id, group_id) VALUES (?, ?)",
                           (user_id, group_id))
            
            flash("Group created successfully and you've been added to it!", "success")
            return redirect(url_for("index"))
        except sqlite3.Error as e:
            flash(f"An error occurred: {e}", "error")
            return render_template("create_group.html")
    
    return render_template("create_group.html")



@app.route("/search_groups", methods=["GET", "POST"])
@login_required
def search_groups():
    groups = []
    postcode = ""
    if request.method == "POST":
        postcode = request.form.get("postcode")
        db = get_db()
        groups = db.execute("SELECT * FROM groups WHERE postcode = ?", (postcode,)).fetchall()
    return render_template("search_groups.html", groups=groups, postcode=postcode)




@app.route("/view_group/<int:group_id>")
@login_required
def view_group(group_id):
    try:
        db = get_db()
        cursor = db.cursor()

        # Fetch group details including member count
        cursor.execute("""
            SELECT g.*, COUNT(ug.user_id) as member_count
            FROM groups g
            LEFT JOIN user_groups ug ON g.id = ug.group_id
            WHERE g.id = ?
            GROUP BY g.id
        """, (group_id,))
        group = cursor.fetchone()

        if group is None:
            flash("Group not found", "error")
            return redirect(url_for("search_groups"))

        # Check if the current user is a member of this group
        cursor.execute("""
            SELECT 1 FROM user_groups
            WHERE user_id = ? AND group_id = ?
        """, (session["user_id"], group_id))
        is_member = cursor.fetchone() is not None

        # Print debug information
        print(f"Group type: {type(group)}")
        print(f"Group contents: {dict(group)}")
        print(f"Is member: {is_member}")

        return render_template("view_group.html", group=group, is_member=is_member)
    except Exception as e:
        print(f"Error in view_group: {str(e)}")
        return f"An error occurred: {str(e)}", 500






@app.route("/add_tradesman/<int:group_id>", methods=["GET", "POST"])
@login_required
def add_tradesman(group_id):
    db = get_db()
    cursor = db.cursor()

    # Check if the user is a member of the group
    cursor.execute("SELECT 1 FROM user_groups WHERE user_id = ? AND group_id = ?", 
                   (session["user_id"], group_id))
    is_member = cursor.fetchone() is not None

    if not is_member:
        flash("You must be a member of the group to add a tradesman.", "error")
        return redirect(url_for("view_group", group_id=group_id))

    if request.method == "POST":
        # Get form data
        trade = request.form.get("trade")
        name = request.form.get("name")
        address = request.form.get("address")
        postcode = request.form.get("postcode")
        phone_number = request.form.get("phone_number")
        email = request.form.get("email")

        # Insert the tradesman into the database
        try:
            cursor.execute("""
                INSERT INTO tradesmen (trade, name, address, postcode, phone_number, email)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (trade, name, address, postcode, phone_number, email))
            db.commit()
            flash("Tradesman added successfully!", "success")
        except Exception as e:
            db.rollback()
            flash(f"An error occurred: {str(e)}", "error")
        
        return redirect(url_for("view_group", group_id=group_id))

    # If it's a GET request, just render the form
    return render_template("add_tradesman.html", group_id=group_id)



if __name__ == '__main__':
    app.run(debug=True)


