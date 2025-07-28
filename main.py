# Configure application
from flask import Flask, g, render_template
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Import configuration
from config import get_config

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
    
    # Add handlers to app logger
    app.logger.addHandler(file_handler)
    app.logger.setLevel(getattr(logging, config.LOG_LEVEL))
    
    # Log application startup
    app.logger.info('Application startup')

def setup_extensions(app: Flask, config):
    """Initialize Flask extensions."""
    # Initialize CSRF protection
    csrf = CSRFProtect(app)
    
    # Initialize session
    Session(app)

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
    """Register database teardown function."""
    # Import database service
    from app.services.database import get_db_service

    @app.teardown_appcontext
    def close_connection(exception):
        """Close database connection on app context teardown."""
        get_db_service().close_connection()

# Create the application instance
app = create_app()

# Legacy function for backward compatibility
def get_db():
    """Legacy function for backward compatibility."""
    from app.services.database import get_db_service
    return get_db_service().get_connection()

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG']) 