"""
Centralized error handlers for the Jobeco application.

This module provides centralized error handling for all application routes.
"""

import logging
from flask import render_template, request, jsonify
from werkzeug.exceptions import HTTPException
from app.exceptions import JobecoException

logger = logging.getLogger(__name__)


def is_ajax_request():
    """Check if the request is an AJAX request."""
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'


def register_error_handlers(app):
    """Register all error handlers with the Flask app."""
    
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request errors."""
        logger.warning(f"Bad request: {request.url} - {error}")
        if is_ajax_request():
            return jsonify({'error': 'Bad request', 'message': str(error)}), 400
        return render_template('errors/400.html'), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        """Handle 401 Unauthorized errors."""
        logger.warning(f"Unauthorized access: {request.url}")
        if is_ajax_request():
            return jsonify({'error': 'Unauthorized', 'message': 'Authentication required'}), 401
        return render_template('errors/401.html'), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        """Handle 403 Forbidden errors."""
        logger.warning(f"Forbidden access: {request.url}")
        if is_ajax_request():
            return jsonify({'error': 'Forbidden', 'message': 'Access denied'}), 403
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors."""
        logger.info(f"Page not found: {request.url}")
        if is_ajax_request():
            return jsonify({'error': 'Not found', 'message': 'Resource not found'}), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(409)
    def conflict(error):
        """Handle 409 Conflict errors."""
        logger.warning(f"Conflict: {request.url} - {error}")
        if is_ajax_request():
            return jsonify({'error': 'Conflict', 'message': str(error)}), 409
        return render_template('errors/409.html'), 409
    
    @app.errorhandler(429)
    def too_many_requests(error):
        """Handle 429 Too Many Requests errors."""
        logger.warning(f"Rate limit exceeded: {request.url}")
        if is_ajax_request():
            return jsonify({'error': 'Too many requests', 'message': 'Rate limit exceeded'}), 429
        return render_template('errors/429.html'), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server Error."""
        logger.error(f"Internal server error: {request.url} - {error}")
        if is_ajax_request():
            return jsonify({'error': 'Internal server error', 'message': 'An unexpected error occurred'}), 500
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(JobecoException)
    def handle_jobeco_exception(error):
        """Handle all Jobeco exceptions."""
        logger.error(f"Jobeco exception: {error.message}")
        
        if is_ajax_request():
            return jsonify({
                'error': error.__class__.__name__,
                'message': error.message,
                'error_code': getattr(error, 'error_code', None)
            }), error.status_code
        
        # For non-AJAX requests, render appropriate error template
        if error.status_code == 404:
            return render_template('errors/404.html'), 404
        elif error.status_code == 403:
            return render_template('errors/403.html'), 403
        elif error.status_code == 401:
            return render_template('errors/401.html'), 401
        elif error.status_code == 400:
            return render_template('errors/400.html'), 400
        else:
            return render_template('errors/500.html'), 500
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """Handle Werkzeug HTTP exceptions."""
        logger.warning(f"HTTP exception: {error.code} - {error.description}")
        
        if is_ajax_request():
            return jsonify({
                'error': error.name,
                'message': error.description
            }), error.code
        
        return render_template(f'errors/{error.code}.html'), error.code
    
    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        """Handle all other exceptions."""
        logger.error(f"Unhandled exception: {type(error).__name__} - {str(error)}")
        
        if is_ajax_request():
            return jsonify({
                'error': 'Internal server error',
                'message': 'An unexpected error occurred'
            }), 500
        
        return render_template('errors/500.html'), 500
    