from flask import Blueprint, flash, redirect, render_template, request, session, url_for
import sqlite3

from helpers import login_required

# Create Blueprint
jobs_bp = Blueprint('jobs', __name__)

@jobs_bp.route("/add_job/<int:tradesman_id>", methods=["GET", "POST"])
@login_required
def add_job(tradesman_id):
    db = get_db()
    cursor = db.cursor()

    # Get tradesman information
    cursor.execute("SELECT first_name, family_name, company_name, trade FROM tradesmen WHERE id = ?", (tradesman_id,))
    tradesman = cursor.fetchone()
    
    if not tradesman:
        flash("Tradesman not found.", "error")
        return redirect(url_for("search.search_tradesmen"))

    if request.method == "POST":
        user_id = session["user_id"]
        date_started = request.form.get("date_started")
        date_finished = request.form.get("date_finished")
        title = request.form.get("title")
        description = request.form.get("description")
        call_out_fee = request.form.get("call_out_fee")
        materials_fee = request.form.get("materials_fee")
        hourly_rate = request.form.get("hourly_rate")
        hours_worked = request.form.get("hours_worked")
        daily_rate = request.form.get("daily_rate")
        days_worked = request.form.get("days_worked")
        total_cost = request.form.get("total_cost")
        rating = request.form.get("rating")

        try:
            # Convert empty strings to None for optional fields
            call_out_fee = call_out_fee if call_out_fee else None
            materials_fee = materials_fee if materials_fee else None
            hourly_rate = hourly_rate if hourly_rate else None
            hours_worked = hours_worked if hours_worked else None
            daily_rate = daily_rate if daily_rate else None
            days_worked = days_worked if days_worked else None
            
            cursor.execute("""
                INSERT INTO jobs (user_id, tradesman_id, type, date_started, date_finished, title, description, call_out_fee, materials_fee, hourly_rate, hours_worked, daily_rate, days_worked, total_cost, rating)
                VALUES (?, ?, 'job', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, tradesman_id, date_started, date_finished, title, description, call_out_fee, materials_fee, hourly_rate, hours_worked, daily_rate, days_worked, total_cost, rating))
            db.commit()
            flash("Job added successfully!", "success")
        except Exception as e:
            db.rollback()
            flash(f"An error occurred: {str(e)}", "error")

        return redirect(url_for("tradesmen.view_tradesman", tradesman_id=tradesman_id))

    return render_template("add_job.html", tradesman_id=tradesman_id, tradesman=tradesman)

@jobs_bp.route("/add_quote/<int:tradesman_id>", methods=["GET", "POST"])
@login_required
def add_quote(tradesman_id):
    db = get_db()
    cursor = db.cursor()

    # Get tradesman information
    cursor.execute("SELECT first_name, family_name, company_name, trade FROM tradesmen WHERE id = ?", (tradesman_id,))
    tradesman = cursor.fetchone()
    
    if not tradesman:
        flash("Tradesman not found.", "error")
        return redirect(url_for("search.search_tradesmen"))

    if request.method == "POST":
        user_id = session["user_id"]
        date_requested = request.form.get("date_requested")
        date_received = request.form.get("date_received")
        title = request.form.get("title")
        description = request.form.get("description")
        call_out_fee = request.form.get("call_out_fee")
        materials_fee = request.form.get("materials_fee")
        hourly_rate = request.form.get("hourly_rate")
        hours_estimated = request.form.get("hours_estimated")
        daily_rate = request.form.get("daily_rate")
        days_estimated = request.form.get("days_estimated")
        total_quote = request.form.get("total_quote")
        status = request.form.get("status", "pending")

        try:
            # Convert empty strings to None for optional fields
            call_out_fee = call_out_fee if call_out_fee else None
            materials_fee = materials_fee if materials_fee else None
            hourly_rate = hourly_rate if hourly_rate else None
            hours_estimated = hours_estimated if hours_estimated else None
            daily_rate = daily_rate if daily_rate else None
            days_estimated = days_estimated if days_estimated else None
            
            cursor.execute("""
                INSERT INTO jobs (user_id, tradesman_id, type, date_requested, date_received, title, description, call_out_fee, materials_fee, hourly_rate, hours_estimated, daily_rate, days_estimated, total_quote, status)
                VALUES (?, ?, 'quote', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, tradesman_id, date_requested, date_received, title, description, call_out_fee, materials_fee, hourly_rate, hours_estimated, daily_rate, days_estimated, total_quote, status))
            db.commit()
            flash("Quote added successfully!", "success")
        except Exception as e:
            db.rollback()
            flash(f"An error occurred: {str(e)}", "error")

        return redirect(url_for("tradesmen.view_tradesman", tradesman_id=tradesman_id))

    return render_template("add_quote.html", tradesman_id=tradesman_id, tradesman=tradesman)

@jobs_bp.route("/convert_quote_to_job/<int:quote_id>", methods=["POST"])
@login_required
def convert_quote_to_job(quote_id):
    """Convert a quote to a job when accepted"""
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Get the quote details
        cursor.execute("""
            SELECT tradesman_id, title, description, call_out_fee, materials_fee, 
                   hourly_rate, hours_estimated, daily_rate, days_estimated, total_quote
            FROM jobs 
            WHERE id = ? AND type = 'quote'
        """, (quote_id,))
        quote = cursor.fetchone()
        
        if not quote:
            flash("Quote not found.", "error")
            return redirect(url_for("search.search_tradesmen"))
        
        # Update the quote status to accepted
        cursor.execute("""
            UPDATE jobs 
            SET status = 'accepted' 
            WHERE id = ?
        """, (quote_id,))
        
        # Create a new job based on the quote
        cursor.execute("""
            INSERT INTO jobs (
                user_id, tradesman_id, type, title, description, 
                call_out_fee, materials_fee, hourly_rate, hours_worked, 
                daily_rate, days_worked, total_cost
            ) VALUES (?, ?, 'job', ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session["user_id"], quote['tradesman_id'], quote['title'], 
            quote['description'], quote['call_out_fee'], quote['materials_fee'],
            quote['hourly_rate'], quote['hours_estimated'], quote['daily_rate'], 
            quote['days_estimated'], quote['total_quote']
        ))
        
        db.commit()
        flash("Quote converted to job successfully!", "success")
        
    except Exception as e:
        db.rollback()
        flash(f"An error occurred: {str(e)}", "error")
    
    return redirect(url_for("tradesmen.view_tradesman", tradesman_id=quote['tradesman_id']))

@jobs_bp.route("/reject_quote/<int:quote_id>", methods=["POST"])
@login_required
def reject_quote(quote_id):
    """Reject a quote"""
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Get the quote details
        cursor.execute("""
            SELECT tradesman_id FROM jobs 
            WHERE id = ? AND type = 'quote'
        """, (quote_id,))
        quote = cursor.fetchone()
        
        if not quote:
            flash("Quote not found.", "error")
            return redirect(url_for("search.search_tradesmen"))
        
        # Update the quote status to declined
        cursor.execute("""
            UPDATE jobs 
            SET status = 'declined' 
            WHERE id = ?
        """, (quote_id,))
        
        db.commit()
        flash("Quote declined successfully!", "success")
        
    except Exception as e:
        db.rollback()
        flash(f"An error occurred: {str(e)}", "error")
    
    return redirect(url_for("tradesmen.view_tradesman", tradesman_id=quote['tradesman_id']))

@jobs_bp.route('/view_quote/<int:quote_id>')
@login_required
def view_quote(quote_id):
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("""
        SELECT j.*, 
               CASE 
                   WHEN t.first_name IS NOT NULL THEN t.first_name || ' ' || t.family_name
                   ELSE t.family_name
               END as tradesman_name, 
               t.trade
        FROM jobs j
        JOIN tradesmen t ON j.tradesman_id = t.id
        WHERE j.id = ? AND j.type = 'quote'
    """, (quote_id,))
    quote = cursor.fetchone()
    
    if quote:
        # Convert row to dictionary using column names
        quote_dict = dict(zip([column[0] for column in cursor.description], quote))
        
        return render_template('view_quote.html', quote=quote_dict)
    else:
        flash('Quote not found.', 'error')
        return redirect(url_for('main.index'))

@jobs_bp.route('/view_job/<int:job_id>')
@login_required
def view_job(job_id):
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("""
        SELECT j.*, 
               CASE 
                   WHEN t.first_name IS NOT NULL THEN t.first_name || ' ' || t.family_name
                   ELSE t.family_name
               END as tradesman_name, 
               t.trade,
               u.username as user_username,
               u.firstname as user_firstname,
               u.lastname as user_lastname
        FROM jobs j
        JOIN tradesmen t ON j.tradesman_id = t.id
        JOIN users u ON j.user_id = u.id
        WHERE j.id = ?
    """, (job_id,))
    job = cursor.fetchone()
    
    if job:
        # Convert row to dictionary using column names
        job_dict = dict(zip([column[0] for column in cursor.description], job))
        
        return render_template('view_job.html', job=job_dict)
    else:
        flash('Job not found.', 'error')
        return redirect(url_for('main.index'))

@jobs_bp.route('/edit_job/<int:job_id>', methods=['GET', 'POST'])
@login_required
def edit_job(job_id):
    db = get_db()
    cursor = db.cursor()
    
    # Get the job with user info to check ownership
    cursor.execute("""
        SELECT j.*, 
               CASE 
                   WHEN t.first_name IS NOT NULL THEN t.first_name || ' ' || t.family_name
                   ELSE t.family_name
               END as tradesman_name, 
               t.trade
        FROM jobs j
        JOIN tradesmen t ON j.tradesman_id = t.id
        WHERE j.id = ?
    """, (job_id,))
    job = cursor.fetchone()
    
    if not job:
        flash('Job not found.', 'error')
        return redirect(url_for('main.index'))
    
    # Check if the current user owns this job
    if job['user_id'] != session['user_id']:
        flash('You can only edit your own jobs.', 'error')
        return redirect(url_for('jobs.view_job', job_id=job_id))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        date_started = request.form.get('date_started', '').strip() or None
        date_finished = request.form.get('date_finished', '').strip() or None
        call_out_fee = request.form.get('call_out_fee', '').strip() or None
        materials_fee = request.form.get('materials_fee', '').strip() or None
        hourly_rate = request.form.get('hourly_rate', '').strip() or None
        hours_worked = request.form.get('hours_worked', '').strip() or None
        daily_rate = request.form.get('daily_rate', '').strip() or None
        days_worked = request.form.get('days_worked', '').strip() or None
        rating = request.form.get('rating', '').strip() or None
        
        # Validate required fields
        if not title:
            flash('Title is required.', 'error')
            return render_template('edit_job.html', job=dict(zip([column[0] for column in cursor.description], job)))
        
        if not description:
            flash('Description is required.', 'error')
            return render_template('edit_job.html', job=dict(zip([column[0] for column in cursor.description], job)))
        
        # Convert numeric fields
        try:
            if call_out_fee:
                call_out_fee = int(call_out_fee)
            if materials_fee:
                materials_fee = int(materials_fee)
            if hourly_rate:
                hourly_rate = int(hourly_rate)
            if hours_worked:
                hours_worked = float(hours_worked)
            if daily_rate:
                daily_rate = int(daily_rate)
            if days_worked:
                days_worked = float(days_worked)
            if rating:
                rating = int(rating)
                if rating < 1 or rating > 5:
                    flash('Rating must be between 1 and 5.', 'error')
                    return render_template('edit_job.html', job=dict(zip([column[0] for column in cursor.description], job)))
        except ValueError:
            flash('Invalid numeric value provided.', 'error')
            return render_template('edit_job.html', job=dict(zip([column[0] for column in cursor.description], job)))
        
        # Calculate total cost
        total_cost = 0
        if call_out_fee:
            total_cost += call_out_fee
        if materials_fee:
            total_cost += materials_fee
        if hourly_rate and hours_worked:
            total_cost += hourly_rate * hours_worked
        if daily_rate and days_worked:
            total_cost += daily_rate * days_worked
        
        # Update the job
        cursor.execute("""
            UPDATE jobs 
            SET title = ?, description = ?, date_started = ?, date_finished = ?,
                call_out_fee = ?, materials_fee = ?, hourly_rate = ?, hours_worked = ?,
                daily_rate = ?, days_worked = ?, total_cost = ?, rating = ?
            WHERE id = ?
        """, (title, description, date_started, date_finished, call_out_fee, materials_fee,
              hourly_rate, hours_worked, daily_rate, days_worked, total_cost, rating, job_id))
        
        db.commit()
        flash('Job updated successfully.', 'success')
        return redirect(url_for('jobs.view_job', job_id=job_id))
    
    # GET request - show edit form
    job_dict = dict(zip([column[0] for column in cursor.description], job))
    return render_template('edit_job.html', job=job_dict)

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