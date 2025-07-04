# Configure application
from flask import Flask, g, render_template
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
import sqlite3
import os
import logging
from logging.handlers import RotatingFileHandler

# Import route blueprints
from app.routes.auth import auth_bp
from app.routes.groups import groups_bp
from app.routes.tradesmen import tradesmen_bp
from app.routes.jobs import jobs_bp
from app.routes.search import search_bp
from app.routes.profile import profile_bp
from app.routes.main import main_bp

app = Flask(__name__)

# Configure logging
if not os.path.exists('logs'):
    os.mkdir('logs')
file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Application startup')

# Configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = "your-secret-key-here-change-in-production"  # Use consistent secret key

# Configure CSRF protection
app.config["WTF_CSRF_ENABLED"] = True
app.config["WTF_CSRF_TIME_LIMIT"] = 3600  # 1 hour

# Initialize CSRF protection
csrf = CSRFProtect(app)

Session(app)



# Import configuration
from app.config import DATABASE

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(groups_bp)
app.register_blueprint(tradesmen_bp)
app.register_blueprint(jobs_bp)
app.register_blueprint(search_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(main_bp)

# Custom error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db = getattr(g, '_database', None)
    if db is not None:
        db.rollback()
    return render_template('500.html'), 500

# Import database service
from app.services.database import get_db_service

def get_db():
    """Legacy function for backward compatibility."""
    return get_db_service().get_connection()

@app.teardown_appcontext
def close_connection(exception):
    """Close database connection on app context teardown."""
    get_db_service().close_connection()

if __name__ == '__main__':
    app.run(debug=True) 