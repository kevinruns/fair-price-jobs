import os
from typing import Optional
from pathlib import Path

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, continue without it
    pass
except Exception:
    # Any other error loading .env file, continue without it
    pass

class Config:
    """Base configuration class with common settings."""
    
    # Application settings
    SECRET_KEY: str = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG: bool = False
    
    # Database settings
    DATABASE: str = os.environ.get('DATABASE') or 'application.db'
    DATABASE_PATH: Optional[str] = None
    
    # File upload settings
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER: str = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    ALLOWED_EXTENSIONS: set = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'txt'}
    
    # Session settings
    SESSION_PERMANENT: bool = False
    SESSION_TYPE: str = 'filesystem'
    SESSION_FILE_DIR: str = os.environ.get('SESSION_FILE_DIR') or 'flask_session'
    
    # CSRF settings
    WTF_CSRF_ENABLED: bool = True
    WTF_CSRF_TIME_LIMIT: int = 3600  # 1 hour
    
    # Logging settings
    LOG_LEVEL: str = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE: str = os.environ.get('LOG_FILE') or 'logs/app.log'
    LOG_MAX_BYTES: int = 10240
    LOG_BACKUP_COUNT: int = 10
    
    # Security settings
    PASSWORD_MIN_LENGTH: int = 6
    MAX_LOGIN_ATTEMPTS: int = 5
    SESSION_TIMEOUT: int = 3600  # 1 hour
    
    # Pagination settings
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100
    
    # OAuth Email settings
    OAUTH_CLIENT_ID: Optional[str] = os.environ.get('OAUTH_CLIENT_ID')
    OAUTH_CLIENT_SECRET: Optional[str] = os.environ.get('OAUTH_CLIENT_SECRET')
    OAUTH_REFRESH_TOKEN: Optional[str] = os.environ.get('OAUTH_REFRESH_TOKEN')
    FROM_EMAIL: Optional[str] = os.environ.get('FROM_EMAIL')
    APP_URL: str = os.environ.get('APP_URL') or 'http://localhost:5000'
    
    # Internationalization settings
    LANGUAGES = {
        'en': 'English',
        'fr': 'Français', 
        'es': 'Español',
        'de': 'Deutsch',
        'it': 'Italiano'
    }
    DEFAULT_LANGUAGE = 'en'
    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_DEFAULT_TIMEZONE = 'UTC'
    
    def __init__(self):
        # Set database path
        if self.DATABASE_PATH is None:
            self.DATABASE_PATH = self.DATABASE

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG: bool = True
    DATABASE: str = 'development.db'
    LOG_LEVEL: str = 'DEBUG'

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG: bool = False
    DATABASE: str = 'production.db'
    LOG_LEVEL: str = 'WARNING'
    SESSION_PERMANENT: bool = True
    SESSION_TIMEOUT: int = 86400  # 24 hours
    PASSWORD_MIN_LENGTH: int = 8
    MAX_LOGIN_ATTEMPTS: int = 3

class TestingConfig(Config):
    """Testing configuration."""
    TESTING: bool = True
    DEBUG: bool = True
    DATABASE: str = ':memory:'
    WTF_CSRF_ENABLED: bool = False
    LOG_LEVEL: str = 'DEBUG'

def get_config(config_name: Optional[str] = None) -> Config:
    """
    Get configuration based on environment or config name.
    
    Args:
        config_name: Configuration name ('development', 'production', 'testing')
    
    Returns:
        Configuration instance
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    configs = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    
    config_class = configs.get(config_name, DevelopmentConfig)
    return config_class()

# Convenience function for getting database path
def get_database_path() -> str:
    """Get the database path from current configuration."""
    db_path = get_config().DATABASE_PATH
    if db_path is None:
        raise ValueError("Database path is not configured")
    return db_path
