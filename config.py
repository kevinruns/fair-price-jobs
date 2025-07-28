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
    
    def __init__(self):
        """Initialize configuration with computed values."""
        # Set database path relative to project root
        if not self.DATABASE_PATH:
            project_root = Path(__file__).parent
            self.DATABASE_PATH = str(project_root / self.DATABASE)
        
        # Ensure log directory exists
        log_dir = Path(self.LOG_FILE).parent
        log_dir.mkdir(exist_ok=True)
        
        # Ensure session directory exists
        session_dir = Path(self.SESSION_FILE_DIR)
        session_dir.mkdir(exist_ok=True)
        
        # Ensure upload directory exists
        upload_dir = Path(self.UPLOAD_FOLDER)
        upload_dir.mkdir(exist_ok=True)

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    
    # Development-specific settings
    DATABASE = 'development.db'
    SESSION_TYPE = 'filesystem'

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    LOG_LEVEL = 'WARNING'
    
    # Production-specific settings
    DATABASE = os.environ.get('DATABASE') or 'production.db'
    
    # Security settings for production
    SESSION_PERMANENT = True
    SESSION_TIMEOUT = 86400  # 24 hours
    
    # Ensure secret key is set in production
    def __init__(self):
        super().__init__()
        secret_key = os.environ.get('SECRET_KEY')
        if not secret_key:
            raise ValueError("SECRET_KEY environment variable must be set in production")
        self.SECRET_KEY = secret_key

class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    
    # Testing-specific settings
    DATABASE = ':memory:'  # Use in-memory database for testing
    WTF_CSRF_ENABLED = False  # Disable CSRF for testing
    SESSION_TYPE = 'filesystem'
    
    def __init__(self):
        super().__init__()
        # Allow database path override for testing
        if os.environ.get('TEST_DATABASE'):
            self.DATABASE = os.environ.get('TEST_DATABASE')
            self.DATABASE_PATH = self.DATABASE

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(config_name: Optional[str] = None) -> Config:
    """
    Get configuration based on environment.
    
    Args:
        config_name: Configuration name ('development', 'production', 'testing')
                    If None, uses FLASK_ENV environment variable
    
    Returns:
        Configuration instance
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    config_class = config.get(config_name, config['default'])
    return config_class()

# Convenience function for getting database path
def get_database_path() -> str:
    """Get the database path from current configuration."""
    db_path = get_config().DATABASE_PATH
    if db_path is None:
        raise ValueError("Database path is not configured")
    return db_path
