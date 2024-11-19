# Configure application
from flask import Flask, g, flash, redirect, render_template, request, session, url_for, jsonify
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
        user_id = session["user_id"]
        
        # Modified query to include user's status in groups
        groups = db.execute("""
            SELECT g.*, 
                   (SELECT COUNT(*) FROM user_groups WHERE group_id = g.id) as member_count,
                   (SELECT COUNT(*) FROM join_requests WHERE group_id = g.id) as pending_requests,                            
                   CASE 
                       WHEN jr.user_id IS NOT NULL THEN 'pending' 
                       WHEN ug.status IS NOT NULL THEN ug.status 
                       ELSE NULL 
                   END as status  -- Use CASE to determine status for the logged-in user
            FROM groups g 
            LEFT JOIN user_groups ug ON g.id = ug.group_id AND ug.user_id = ?  -- Join with user_groups for the logged-in user
            LEFT JOIN join_requests jr ON g.id = jr.group_id AND jr.user_id = ?  -- Check for pending requests for the logged-in user
        """, (user_id, user_id)).fetchall()
        
        # Add this debug print
        print("Groups data:", [dict(row) for row in groups])

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
                db.execute("INSERT INTO user_groups (user_id, group_id, status) VALUES (?, ?, ?)",
                           (user_id, group_id, "creator"))
            
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
        user_id = session.get("user_id")  # Assuming user_id is stored in session
        db = get_db()
        groups = db.execute("""
            SELECT g.*, 
                   (SELECT COUNT(*) FROM user_groups WHERE group_id = g.id) as member_count,
                   CASE 
                       WHEN jr.user_id IS NOT NULL THEN 'pending' 
                       WHEN ug.status IS NOT NULL THEN ug.status 
                       ELSE NULL 
                   END as status  -- Use CASE to determine status for the logged-in user
            FROM groups g 
            LEFT JOIN user_groups ug ON g.id = ug.group_id AND ug.user_id = ?  -- Join with user_groups for the logged-in user
            LEFT JOIN join_requests jr ON g.id = jr.group_id AND jr.user_id = ?  -- Check for pending requests for the logged-in user
            WHERE g.postcode = ? OR g.postcode LIKE ? || '%'  -- Search by postcode
            GROUP BY g.id  -- Group by group ID to ensure each group is returned once
        """, (user_id, user_id, postcode, postcode)).fetchall()  # Pass user_id and postcode as parameters
        
        # Add this debug print
        print("Groups data:", [dict(row) for row in groups])
        
    return render_template("search_groups.html", groups=groups, postcode=postcode)




# do I need POST?
@app.route("/view_group/<int:group_id>", methods=['GET', 'POST'])
@login_required
def view_group(group_id):
    db = get_db()
    cursor = db.cursor()
    user_id = session["user_id"]

    # Handle POST request (button submission)
    if request.method == 'POST':
        try:
            cursor.execute("INSERT INTO join_requests (user_id, group_id) VALUES (?, ?)", 
                         (user_id, group_id))
            db.commit()
            flash("Join request sent successfully!", "success")
        except sqlite3.IntegrityError:
            flash("You have already requested to join this group.", "warning")
        except Exception as e:
            db.rollback()
            flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('view_group', group_id=group_id))

    # Fetch group information
    cursor.execute("SELECT * FROM groups WHERE id = ?", (group_id,))
    group = cursor.fetchone()

    if group:
        group = dict(zip([column[0] for column in cursor.description], group))
        
        # Check if the user is a member of the group
        cursor.execute("SELECT 1 FROM user_groups WHERE user_id = ? AND group_id = ?", (user_id, group_id))
        is_member = cursor.fetchone() is not None

        # Check for pending join request
        cursor.execute("""
            SELECT 1 FROM join_requests 
            WHERE user_id = ? AND group_id = ?
        """, (user_id, group_id))
        pending_request = cursor.fetchone() is not None

        # Fetch member count
        cursor.execute("SELECT COUNT(*) FROM user_groups WHERE group_id = ?", (group_id,))
        member_count = cursor.fetchone()[0]

        group['member_count'] = member_count

        # Fetch tradesmen for this group, sorted by trade
        cursor.execute("""
            SELECT t.* 
            FROM tradesmen t
            JOIN group_tradesmen gt ON t.id = gt.tradesman_id
            WHERE gt.group_id = ?
            ORDER BY t.trade, t.name
        """, (group_id,))
        tradesmen = cursor.fetchall()

        # Convert tradesmen to a list of dictionaries for easier handling in the template
        tradesmen = [dict(zip([column[0] for column in cursor.description], row)) for row in tradesmen]

        return render_template("view_group.html", 
                            group=group, 
                            is_member=is_member,
                            pending_request=pending_request,
                            tradesmen=tradesmen)
    else:
        flash("Group not found.", "error")
        return redirect(url_for("search_groups"))







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
            
            tradesman_id = cursor.lastrowid  # Get the ID of the newly inserted tradesman
            
            # Add the relationship to group_tradesmen table
            cursor.execute("""
                INSERT INTO group_tradesmen (group_id, tradesman_id)
                VALUES (?, ?)
            """, (group_id, tradesman_id))
            
            db.commit()
            flash("Tradesman added successfully!", "success")
        except Exception as e:
            db.rollback()
            flash(f"An error occurred: {str(e)}", "error")
        
        return redirect(url_for("view_group", group_id=group_id))

    # If it's a GET request, just render the form
    return render_template("add_tradesman.html", group_id=group_id)



@app.route("/tradesman/<int:tradesman_id>")
@login_required
def view_tradesman(tradesman_id):
    try:
        db = get_db()
        cursor = db.cursor()

        # Fetch tradesman details
        cursor.execute("SELECT * FROM tradesmen WHERE id = ?", (tradesman_id,))
        tradesman = cursor.fetchone()

        print(f"Debug: Raw tradesman data: {tradesman}")  # Add this line

        if not tradesman:
            flash("Tradesman not found.", "error")
            return redirect(url_for("search_groups"))

        # Convert tradesman to a dictionary
        tradesman = dict(zip([column[0] for column in cursor.description], tradesman))

        print(f"Debug: Tradesman dictionary: {tradesman}")  # Add this line

        # Fetch jobs for this tradesman
        cursor.execute("""
            SELECT id, date, title, description, total_cost, rating
            FROM jobs
            WHERE tradesman_id = ?
            ORDER BY date DESC
        """, (tradesman_id,))
        jobs = cursor.fetchall()

        # Convert jobs to dictionaries for easier handling in the template
        jobs = [dict(zip([column[0] for column in cursor.description], row)) for row in jobs]

        return render_template("view_tradesman.html", tradesman=tradesman, jobs=jobs)
    except Exception as e:
        print(f"Error in view_tradesman: {str(e)}")
        flash("An error occurred while fetching tradesman data.", "error")
        return redirect(url_for("search_groups"))



@app.route("/add_job/<int:tradesman_id>", methods=["GET", "POST"])
@login_required
def add_job(tradesman_id):
    if request.method == "POST":
        user_id = session["user_id"]  # Assuming you store user_id in session
        date = request.form.get("date")
        title = request.form.get("title")
        description = request.form.get("description")
        call_out_fee = request.form.get("call_out_fee")
        hourly_rate = request.form.get("hourly_rate")
        daily_rate = request.form.get("daily_rate")
        total_cost = request.form.get("total_cost")
        rating = request.form.get("rating")

        db = get_db()
        cursor = db.cursor()

        try:
            cursor.execute("""
                INSERT INTO jobs (user_id, tradesman_id, date, title, description, call_out_fee, hourly_rate, daily_rate, total_cost, rating)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, tradesman_id, date, title, description, call_out_fee, hourly_rate, daily_rate, total_cost, rating))
            db.commit()
            flash("Job added successfully!", "success")
        except Exception as e:
            db.rollback()
            flash(f"An error occurred: {str(e)}", "error")

        return redirect(url_for("view_tradesman", tradesman_id=tradesman_id))

    return render_template("add_job.html", tradesman_id=tradesman_id)



@app.route('/view_job/<int:job_id>')
@login_required
def view_job(job_id):
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("""
        SELECT * FROM jobs 
        WHERE id = ?
    """, (job_id,))
    job = cursor.fetchone()
    
    if job:
        # Convert row to dictionary using column names
        job_dict = dict(zip([column[0] for column in cursor.description], job))
        
        # Debug print to see what data we're getting
        print("Job data:", job_dict)
        
        return render_template('view_job.html', job=job_dict)
    else:
        flash('Job not found.', 'error')
        return redirect(url_for('index'))


@app.route("/view_requests/<int:group_id>")
@login_required
def view_requests(group_id):
    db = get_db()
    
    # Fetch the group name separately
    group = db.execute("""
        SELECT name FROM groups WHERE id = ?
    """, (group_id,)).fetchone()
    
    # Fetch the requests
    requests = db.execute("""
        SELECT jr.id, u.username, u.email
        FROM join_requests jr
        JOIN users u ON jr.user_id = u.id
        WHERE jr.group_id = ?
    """, (group_id,)).fetchall()
    
    return render_template("view_requests.html", requests=requests, group_name=group['name'])


@app.route('/handle_request/<int:request_id>/<action>', methods=['POST'])
@login_required
def handle_request(request_id, action):
    db = get_db()
    
    # Get the request details
    request_data = db.execute("SELECT user_id, group_id FROM join_requests WHERE id = ?", (request_id,)).fetchone()
    
    if action == 'accept':
        
        if request_data:
            user_id = request_data['user_id']
            group_id = request_data['group_id']
            
            # Add user to user_groups table
            db.execute("INSERT INTO user_groups (user_id, group_id, status) VALUES (?, ?, 'member')", (user_id, group_id))
            
            # Remove the request from join_requests table
            db.execute("DELETE FROM join_requests WHERE id = ?", (request_id,))
            
            db.commit()
            flash('Request accepted and user added to the group.', 'success')
        else:
            flash('Request not found.', 'danger')
    
    elif action == 'reject':
        # Remove the request from join_requests table
        db.execute("DELETE FROM join_requests WHERE id = ?", (request_id,))
        db.commit()
        flash('Request rejected.', 'info')
    
    return redirect(url_for('view_requests', group_id=request_data['group_id']))



@app.route("/group_members/<int:group_id>")
@login_required
def group_members(group_id):
    db = get_db()
    members = db.execute("""
        SELECT u.username, u.firstname, u.lastname, u.email 
        FROM user_groups ug
        JOIN users u ON ug.user_id = u.id
        WHERE ug.group_id = ?
    """, (group_id,)).fetchall()
    

    group_name_result = db.execute("""
        SELECT name 
        FROM groups 
        WHERE id = ?
    """, (group_id,)).fetchone()

    group_name = group_name_result['name'] if group_name_result else "Unknown Group"  # Default if not found

    print("Groups data:", [dict(row) for row in members])


    return render_template("group_members.html", members=members, group_id=group_id, group_name=group_name)




if __name__ == '__main__':
    app.run(debug=True)



