"""
Centralized error handlers for the Fair Price application.
"""

import logging
from typing import Any, Dict, Optional, Callable
from functools import wraps
from flask import render_template, request, jsonify, flash, redirect, url_for, Flask
from app.exceptions import FairPriceException, ValidationError, AuthenticationError, AuthorizationError, NotFoundError, DatabaseError, DuplicateResourceError, RateLimitError

logger = logging.getLogger(__name__)

def register_error_handlers(app: Flask) -> None:
    """Register all error handlers with the Flask app."""
    
    @app.errorhandler(400)
    def bad_request(error: Any) -> tuple[str, int]:
        """Handle 400 Bad Request errors."""
        return render_template('errors/400.html'), 400
    
    @app.errorhandler(401)
    def unauthorized(error: Any) -> Any:
        """Handle 401 Unauthorized errors."""
        flash("Please log in to access this page.", "error")
        return redirect(url_for('auth.login'))
    
    @app.errorhandler(403)
    def forbidden(error: Any) -> tuple[str, int]:
        """Handle 403 Forbidden errors."""
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(404)
    def not_found(error: Any) -> tuple[str, int]:
        """Handle 404 Not Found errors."""
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(409)
    def conflict(error: Any) -> tuple[str, int]:
        """Handle 409 Conflict errors."""
        return render_template('errors/409.html'), 409
    
    @app.errorhandler(429)
    def too_many_requests(error: Any) -> tuple[str, int]:
        """Handle 429 Too Many Requests errors."""
        return render_template('errors/429.html'), 429
    
    @app.errorhandler(500)
    def internal_error(error: Any) -> tuple[str, int]:
        """Handle 500 Internal Server Error."""
        # Log the error
        logger.error(f"Internal server error: {error}")
        
        # Rollback database transaction if needed
        from flask import g
        db = getattr(g, '_database', None)
        if db is not None:
            try:
                db.rollback()
            except Exception as rollback_error:
                logger.error(f"Failed to rollback database: {rollback_error}")
        
        return render_template('errors/500.html'), 500
    
    # Custom exception handlers
    @app.errorhandler(ValidationError)
    def handle_validation_error(error: ValidationError) -> Any:
        """Handle validation errors."""
        flash(error.message, "error")
        
        # Redirect back to the form if it's a POST request
        if request.method == "POST":
            return redirect(request.url)
        
        return render_template('errors/400.html', error=error), 400
    
    @app.errorhandler(AuthenticationError)
    def handle_authentication_error(error: AuthenticationError) -> Any:
        """Handle authentication errors."""
        flash(error.message, "error")
        return redirect(url_for('auth.login'))
    
    @app.errorhandler(AuthorizationError)
    def handle_authorization_error(error: AuthorizationError) -> tuple[str, int]:
        """Handle authorization errors."""
        flash(error.message, "error")
        return render_template('errors/403.html', error=error), 403
    
    @app.errorhandler(NotFoundError)
    def handle_not_found_error(error: NotFoundError) -> tuple[str, int]:
        """Handle not found errors."""
        return render_template('errors/404.html', error=error), 404
    
    @app.errorhandler(DatabaseError)
    def handle_database_error(error: DatabaseError) -> tuple[str, int]:
        """Handle database errors."""
        logger.error(f"Database error: {error.message}")
        flash("A database error occurred. Please try again.", "error")
        return render_template('errors/500.html', error=error), 500
    
    @app.errorhandler(DuplicateResourceError)
    def handle_duplicate_resource_error(error: DuplicateResourceError) -> tuple[str, int]:
        """Handle duplicate resource errors."""
        flash(error.message, "error")
        return render_template('errors/409.html', error=error), 409
    
    @app.errorhandler(RateLimitError)
    def handle_rate_limit_error(error: RateLimitError) -> tuple[str, int]:
        """Handle rate limit errors."""
        flash(error.message, "error")
        return render_template('errors/429.html', error=error), 429
    
    @app.errorhandler(FairPriceException)
    def handle_fair_price_exception(error: FairPriceException) -> tuple[str, int]:
        """Handle all other Fair Price exceptions."""
        logger.error(f"Fair Price exception: {error.message}")
        flash(error.message, "error")
        return render_template('errors/500.html', error=error), error.status_code
    
    @app.errorhandler(Exception)
    def handle_generic_exception(error: Exception) -> tuple[str, int]:
        """Handle all other exceptions."""
        logger.error(f"Unhandled exception: {error}", exc_info=True)
        flash("An unexpected error occurred. Please try again.", "error")
        return render_template('errors/500.html'), 500

def log_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
    """Log an error with additional context."""
    error_data = {
        'error_type': type(error).__name__,
        'error_message': str(error),
        'url': request.url,
        'method': request.method,
        'user_agent': request.headers.get('User-Agent'),
        'ip_address': request.remote_addr
    }
    
    if context:
        error_data.update(context)
    
    logger.error(f"Application error: {error_data}")

def handle_database_operation(func: Callable) -> Callable:
    """Decorator to handle database operations with proper error handling."""
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Database operation failed in {func.__name__}: {e}")
            raise DatabaseError(f"Database operation failed: {str(e)}")
    
    return wrapper 