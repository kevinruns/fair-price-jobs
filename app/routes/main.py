from flask import Blueprint, render_template, request, flash, redirect, url_for, session, current_app, abort
from flask_babel import gettext as _
from werkzeug.wrappers.response import Response
from typing import Any, Dict, List, Union, Optional
from app.helpers import login_required
from app.services.user_service import UserService
from app.services.group_service import GroupService
from app.services.tradesman_service import TradesmanService
from app.services.job_service import JobService
from app.services.file_service import FileService
from config import get_config
from pathlib import Path
import os
import babel
from datetime import datetime

main_bp = Blueprint('main', __name__)

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
def get_locale():
    """Get the locale for the current request."""
    # This will be called by Babel, so we need to access app differently
    from flask import current_app, request, session
    
    # Skip locale detection for static files
    if request.path.startswith('/static/'):
        return current_app.config['DEFAULT_LANGUAGE']
    
    # Check URL parameter first
    language = request.args.get('lang')
    if language and language in current_app.config['LANGUAGES']:
        return language
    
    # Check session as fallback
    language = session.get('language')
    if language and language in current_app.config['LANGUAGES']:
        return language
    
    # Check browser preference
    language = request.accept_languages.best_match(current_app.config['LANGUAGES'].keys())
    if language:
        return language
    
    # Default to English
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

def setup_extensions(app: Flask, config):
    """Initialize Flask extensions."""
    # Initialize CSRF protection
    csrf = CSRFProtect(app)
    
    # Initialize session
    Session(app)
    
    # Define locale selector function
    def locale_selector():
        """Modern locale selection with clean fallbacks."""
        # Skip locale detection for static files
        if request.path.startswith('/static/'):
            return app.config['DEFAULT_LANGUAGE']
        
        # 1. URL parameter (primary, immediate)
        if language := request.args.get('lang'):
            if language in app.config['LANGUAGES']:
                return language
        
        # 2. User preference cookie (persistence across visits)
        if language := request.cookies.get('preferred_language'):
            if language in app.config['LANGUAGES']:
                return language
        
        # 3. Browser preference (respectful)
        if language := request.accept_languages.best_match(app.config['LANGUAGES'].keys()):
            return language
        
        # 4. Default
        return app.config['DEFAULT_LANGUAGE']
    
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

@main_bp.route("/")
@login_required
def index() -> Union[str, Response]:
    """Show portfolio of tradesmen and recent jobs."""
    user_service = UserService()
    group_service = GroupService()
    tradesman_service = TradesmanService()
    job_service = JobService()
    
    user_id = session.get("user_id")
    if user_id is None:
        flash(_("User not logged in."), "error")
        return redirect(url_for("auth.login"))
    
    # Get user's tradesmen
    user_tradesmen = tradesman_service.get_tradesmen_by_user(user_id)
    
    # Get user's groups
    user_groups = group_service.get_user_groups_with_stats(user_id, limit=10)
    
    # Get recent jobs for user's tradesmen
    recent_jobs = job_service.get_recent_completed_jobs_for_user(user_id, limit=5)
    
    # Get statistics
    stats = {
        'total_tradesmen': len(user_tradesmen),
        'total_groups': len(user_groups),
        'total_jobs': len(recent_jobs)
    }
    
    return render_template("index.html", 
                         tradesmen=user_tradesmen, 
                         my_groups=user_groups, 
                         recent_jobs=recent_jobs,
                         stats=stats,
                         config=current_app.config)

@main_bp.route('/set_language/<language>')
def set_language(language: str) -> Response:
    """Modern language switching with optional persistence."""
    if language not in current_app.config.get('LANGUAGES', {}):
        flash(_('Invalid language selected.'), 'error')
        return redirect(url_for('main.index'))
    
    # Primary: URL parameter (immediate, shareable)
    response = redirect(f"{url_for('main.index')}?lang={language}")
    
    # Optional: Set cookie for convenience (modern approach)
    response.set_cookie(
        'preferred_language', 
        language,
        max_age=365*24*60*60,  # 1 year
        samesite='Lax',
        secure=request.is_secure,
        httponly=False  # Allow JS access for modern features
    )
    
    return response

@main_bp.route('/test_session')
def test_session():
    """Test route to see session contents."""
    return {
        'session_language': session.get('language', 'None'),
        'session_id': session.get('_id', 'None'),
        'all_session': dict(session),
        'available_languages': current_app.config.get('LANGUAGES', {})
    }

@main_bp.route('/init_db')
def initialize_db() -> Union[str, tuple[str, int]]:
    """Initialize the database with schema."""
    from app.services.database import get_db_service
    
    config = get_config()
    db_service = get_db_service()
    
    try:
        schema_path = Path(__file__).parent.parent.parent / 'sql' / 'schema.sql'
        db_service.init_db(schema_path)
        return _("Database initialized successfully!")
    except Exception as e:
        return _("Error initializing database: {}").format(str(e)), 500

@main_bp.route('/uploads/<path:filename>')
@login_required
def uploaded_file(filename):
    """Serve uploaded files."""
    from flask import send_from_directory
    
    # Security check - ensure filename doesn't contain path traversal
    if '..' in filename or filename.startswith('/'):
        abort(404)
    
    upload_folder = current_app.config['UPLOAD_FOLDER']
    return send_from_directory(upload_folder, filename)

@main_bp.route('/test_translation')
def test_translation():
    """Test route to verify translations are working."""
    from flask_babel import get_locale
    current_locale = get_locale()
    
    test_strings = {
        'Home': _('Home'),
        'Jobs & Quotes': _('Jobs & Quotes'),
        'Tradesmen': _('Tradesmen'),
        'Groups': _('Groups')
    }
    
    return {
        'current_locale': str(current_locale),
        'session_language': session.get('language', 'None'),
        'translations': test_strings
    }

@main_bp.route('/debug_babel')
def debug_babel():
    """Debug Babel configuration."""
    from flask_babel import get_locale, gettext
    
    return {
        'current_locale': str(get_locale()),
        'session_language': session.get('language', 'None'),
        'available_languages': list(current_app.config['LANGUAGES'].keys()),
        'default_language': current_app.config['DEFAULT_LANGUAGE'],
        'babel_default_locale': current_app.config['BABEL_DEFAULT_LOCALE'],
        'test_translation': gettext('Home'),
        'translation_dir_exists': os.path.exists('translations'),
        'fr_mo_exists': os.path.exists('translations/fr/LC_MESSAGES/messages.mo'),
        'fr_mo_size': os.path.getsize('translations/fr/LC_MESSAGES/messages.mo') if os.path.exists('translations/fr/LC_MESSAGES/messages.mo') else 0
    }

@main_bp.route('/test_translation_simple')
def test_translation_simple():
    """Simple test to see if translations work in Python code."""
    from flask_babel import gettext, get_locale
    
    # Test translations in Python
    home_en = gettext('Home')
    
    return {
        'home_translation': home_en,
        'current_locale': str(get_locale()),
        'session_language': session.get('language', 'None')
    }

@main_bp.route('/debug_translations')
def debug_translations():
    """Comprehensive debug of translation system."""
    from flask_babel import gettext, get_locale
    
    # Test translations in Python code
    home_en = gettext('Home')
    
    # Test locale detection
    current_locale = get_locale()
    
    # Test session
    session_lang = session.get('language', 'None')
    
    # Test if translation files are loaded
    try:
        import babel.messages
        # This will show if Babel can find the translation files
        translation_dir = 'translations'
        fr_mo_path = f'{translation_dir}/fr/LC_MESSAGES/messages.mo'
        fr_mo_exists = os.path.exists(fr_mo_path)
        fr_mo_size = os.path.getsize(fr_mo_path) if fr_mo_exists else 0
    except Exception as e:
        fr_mo_exists = False
        fr_mo_size = 0
    
    return {
        'python_translation': home_en,
        'current_locale': str(current_locale),
        'session_language': session_lang,
        'fr_mo_exists': fr_mo_exists,
        'fr_mo_size': fr_mo_size,
        'available_languages': list(current_app.config['LANGUAGES'].keys()),
        'babel_default_locale': current_app.config['BABEL_DEFAULT_LOCALE']
    }

@main_bp.route('/debug_locale_selector')
def debug_locale_selector():
    """Debug the locale selector registration."""
    from flask_babel import get_locale
    
    # Check if the locale selector is properly registered
    try:
        # Try to get the current locale
        current_locale = get_locale()
        
        # Check if babel.locale_selector is set
        babel_locale_selector = hasattr(babel, 'locale_selector')
        
        return {
            'current_locale': str(current_locale),
            'babel_has_locale_selector': babel_locale_selector,
            'babel_locale_selector_type': type(babel.locale_selector).__name__ if babel_locale_selector else 'None',
            'request_args': dict(request.args),
            'session_language': session.get('language', 'None'),
            'available_languages': list(current_app.config['LANGUAGES'].keys())
        }
    except Exception as e:
        return {
            'error': str(e),
            'error_type': type(e).__name__
        }

@main_bp.route('/debug_locale_selector_after_fix')
def debug_locale_selector_after_fix():
    """Debug the locale selector registration after the fix."""
    return {
        'babel_has_locale_selector': hasattr(babel, 'locale_selector'),
        'babel_locale_selector_type': type(babel.locale_selector).__name__ if hasattr(babel, 'locale_selector') else 'None',
        'babel_app_initialized': hasattr(babel, '_app'),
        'babel_extensions': list(babel._app.extensions.keys()) if hasattr(babel, '_app') else [],
        'flask_extensions': list(current_app.extensions.keys()),
        'babel_in_flask_extensions': 'babel' in current_app.extensions
    }

@main_bp.route('/test_translation_after_fix')
def test_translation_after_fix():
    """Test if translations work in Python after the fix."""
    from flask_babel import gettext, get_locale
    
    return {
        'current_locale': str(get_locale()),
        'home_translation': gettext('Home'),
        'jobs_translation': gettext('Jobs & Quotes'),
        'tradesmen_translation': gettext('Tradesmen'),
        'groups_translation': gettext('Groups'),
        'session_language': session.get('language', 'None'),
        'request_args': dict(request.args)
    }

@main_bp.route('/test_template_translation')
def test_template_translation():
    """Test if _() function works in templates."""
    return render_template('test_translation.html')

@main_bp.route('/debug_babel_config')
def debug_babel_config():
    """Debug Babel configuration."""
    return {
        'babel_default_locale': current_app.config.get('BABEL_DEFAULT_LOCALE'),
        'babel_default_timezone': current_app.config.get('BABEL_DEFAULT_TIMEZONE'),
        'languages': current_app.config.get('LANGUAGES'),
        'default_language': current_app.config.get('DEFAULT_LANGUAGE'),
        'translation_dir_exists': os.path.exists('translations'),
        'fr_mo_exists': os.path.exists('translations/fr/LC_MESSAGES/messages.mo'),
        'fr_mo_size': os.path.getsize('translations/fr/LC_MESSAGES/messages.mo') if os.path.exists('translations/fr/LC_MESSAGES/messages.mo') else 0,
        'babel_app_config': {k: v for k, v in current_app.config.items() if 'babel' in k.lower() or 'locale' in k.lower()}
    }

@main_bp.route('/debug_babel_object')
def debug_babel_object():
    """Debug the Babel object itself."""
    return {
        'babel_type': type(babel).__name__,
        'babel_attributes': [attr for attr in dir(babel) if not attr.startswith('_')],
        'babel_locale_selector_exists': hasattr(babel, 'locale_selector'),
        'babel_localeselector_exists': hasattr(babel, 'localeselector'),
        'babel_app_exists': hasattr(babel, '_app'),
        'babel_app_type': type(babel._app).__name__ if hasattr(babel, '_app') else 'None'
    }

@main_bp.route('/debug_babel_capabilities')
def debug_babel_capabilities():
    """Debug what Flask-Babel 4.0.0 can actually do."""
    from flask_babel import gettext, get_locale, format_date, format_datetime
    from datetime import datetime
    
    try:
        current_locale = get_locale()
        locale_str = str(current_locale) if current_locale else 'None'
    except Exception as e:
        locale_str = f"Error: {str(e)}"
    
    try:
        date_formatted = format_date(datetime.now())
    except Exception as e:
        date_formatted = f"Error: {str(e)}"
    
    try:
        default_locale_str = str(babel.default_locale) if babel.default_locale else 'None'
    except Exception as e:
        default_locale_str = f"Error: {str(e)}"
    
    try:
        default_timezone_str = str(babel.default_timezone) if babel.default_timezone else 'None'
    except Exception as e:
        default_timezone_str = f"Error: {str(e)}"
    
    return {
        'babel_attributes': [attr for attr in dir(babel) if not attr.startswith('_')],
        'gettext_works': gettext('Home'),
        'get_locale_works': locale_str,
        'format_date_works': date_formatted,
        'babel_default_locale': default_locale_str,
        'babel_default_timezone': default_timezone_str,
        'flask_babel_version': '4.0.0'
    }

@main_bp.route('/test_babel_locale_change')
def test_babel_locale_change():
    """Test if we can change the Babel locale."""
    from flask_babel import gettext, get_locale
    
    # Test current state
    current_locale = str(get_locale())
    home_translation = gettext('Home')
    
    # Try to change locale by setting babel.default_locale
    original_locale = babel.default_locale
    babel.default_locale = 'fr'
    
    # Test after change
    new_locale = str(get_locale())
    new_home_translation = gettext('Home')
    
    # Restore original
    babel.default_locale = original_locale
    
    return {
        'original_locale': current_locale,
        'original_translation': home_translation,
        'new_locale': new_locale,
        'new_translation': new_home_translation,
        'locale_changed': current_locale != new_locale,
        'translation_changed': home_translation != new_home_translation
    }

@main_bp.route('/test_babel_alternative')
def test_babel_alternative():
    """Test alternative Flask-Babel 4.0.0 approaches."""
    from flask_babel import gettext, get_locale
    from babel import Locale
    
    # Test 1: Try to create a French locale directly
    try:
        fr_locale = Locale('fr')
        fr_home = gettext('Home', locale=fr_locale)
    except Exception as e:
        fr_home = f"Error: {str(e)}"
    
    # Test 2: Check if we can use domain_instance
    try:
        domain_info = str(babel.domain_instance) if babel.domain_instance else 'None'
    except Exception as e:
        domain_info = f"Error: {str(e)}"
    
    # Test 3: Check current state
    current_locale = str(get_locale())
    current_home = gettext('Home')
    
    return {
        'current_locale': current_locale,
        'current_home': current_home,
        'fr_home_direct': fr_home,
        'domain_instance': domain_info,
        'babel_attributes': [attr for attr in dir(babel) if not attr.startswith('_')]
    }

 