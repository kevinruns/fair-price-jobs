# Import the new configuration system
from config import get_config, get_database_path

# Get current configuration
config = get_config()

# Backward compatibility - export DATABASE for existing code
DATABASE = config.DATABASE_PATH

# Export configuration for use in the application
__all__ = ['config', 'DATABASE', 'get_config', 'get_database_path'] 