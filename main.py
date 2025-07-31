# Configure application
from flask import Flask, g, render_template, request, session, current_app, redirect, url_for, flash, Response
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
from flask_babel import Babel
import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Import configuration
from config import get_config

# Create Babel instance at module level
babel = Babel()

# Define locale selector function at module level
def locale_selector():
    """Modern locale selection with clean fallbacks."""
    # Skip locale detection for static files
    if request.path.startswith('/static/'):
        return current_app.config['DEFAULT_LANGUAGE']
    
    # 1. URL parameter (primary, immediate)
    if language := request.args.get('lang'):
        if language in current_app.config['LANGUAGES']:
            return language
    
    # 2. User preference cookie (persistence across visits)
    if language := request.cookies.get('preferred_language'):
        if language in current_app.config['LANGUAGES']:
            return language
    
    # 3. Browser preference (respectful)
    if language := request.accept_languages.best_match(current_app.config['LANGUAGES'].keys()):
        return language
    
    # 4. Default
    return current_app.config['DEFAULT_LANGUAGE']

def create_app(config_name: str = None):
    """
    Application factory function.
    
    Args:
        config_name: Configuration name ('development', 'production', 'testing')
    
    Returns:
        Flask application instance
    """
    # Get configuration
    config = get_config(config_name)
    
    # DEBUG: Print which database is being used
    print(f"Using database: {config.DATABASE_PATH}")
    
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration into Flask app
    app.config.from_object(config)
    
    # Configure logging
    setup_logging(app, config)
    
    # Initialize extensions
    setup_extensions(app, config)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register database teardown
    register_database_teardown(app)
    
    return app

def setup_logging(app: Flask, config):
    """Configure application logging."""
    # Ensure logs directory exists
    log_dir = Path(config.LOG_FILE).parent
    log_dir.mkdir(exist_ok=True)
    
    # Configure file handler
    file_handler = RotatingFileHandler(
        config.LOG_FILE, 
        maxBytes=config.LOG_MAX_BYTES, 
        backupCount=config.LOG_BACKUP_COUNT
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(getattr(logging, config.LOG_LEVEL))
    
    # Add handler to app logger
    app.logger.addHandler(file_handler)
    app.logger.setLevel(getattr(logging, config.LOG_LEVEL))
    app.logger.info('Application startup')

def setup_extensions(app: Flask, config):
    """Initialize Flask extensions."""
    # Initialize CSRF protection
    csrf = CSRFProtect(app)
    
    # Initialize session
    Session(app)
    
    # Initialize Babel for internationalization with locale selector
    babel.init_app(app, locale_selector=locale_selector)
    
    # Add context processor to make config available in templates
    @app.context_processor
    def inject_config():
        return dict(config=app.config)
    
    # Add context processor to make _() function available in templates
    @app.context_processor
    def inject_gettext():
        from flask_babel import gettext
        return dict(_=gettext)
    
    # Add context processor to make current locale available in templates
    @app.context_processor
    def inject_current_locale():
        from flask_babel import get_locale
        return dict(current_locale=str(get_locale()))

def register_blueprints(app: Flask):
    """Register Flask blueprints."""
    # Import route blueprints
    from app.routes.auth import auth_bp
    from app.routes.groups import groups_bp
    from app.routes.tradesmen import tradesmen_bp
    from app.routes.jobs import jobs_bp
    from app.routes.search import search_bp
    from app.routes.profile import profile_bp
    from app.routes.main import main_bp
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(groups_bp)
    app.register_blueprint(tradesmen_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(main_bp)

def register_error_handlers(app: Flask):
    """Register centralized error handlers."""
    from app.error_handlers import register_error_handlers as register_app_error_handlers
    register_app_error_handlers(app)

def register_database_teardown(app: Flask):
    """Register database teardown context."""
    from app.services.database import get_db_service
    
    @app.teardown_appcontext
    def close_db(error):
        db_service = get_db_service()
        db_service.close_connection()

# Create app instance
app = create_app()

@app.before_request
def before_request():
    pass

if __name__ == '__main__':
    app.run(debug=True) 