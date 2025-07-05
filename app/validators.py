"""
Input validation utilities for the Fair Price application.
"""

import re
from typing import Any, Dict, List, Optional, Union
from functools import wraps
from flask import request, flash, redirect, url_for
from app.exceptions import ValidationError

class Validator:
    """Base validator class."""
    
    def __init__(self, field_name: str, required: bool = True):
        self.field_name = field_name
        self.required = required
    
    def validate(self, value: Any) -> Any:
        """Validate a value and return the cleaned value."""
        if value is None or value == "":
            if self.required:
                raise ValidationError(f"{self.field_name} is required", self.field_name)
            return None
        return self._validate(value)
    
    def _validate(self, value: Any) -> Any:
        """Override this method in subclasses."""
        return value

class StringValidator(Validator):
    """Validates string fields."""
    
    def __init__(self, field_name: str, min_length: int = None, max_length: int = None, 
                 pattern: str = None, required: bool = True):
        super().__init__(field_name, required)
        self.min_length = min_length
        self.max_length = max_length
        self.pattern = pattern
    
    def _validate(self, value: str) -> str:
        if not isinstance(value, str):
            raise ValidationError(f"{self.field_name} must be a string", self.field_name)
        
        value = value.strip()
        
        if self.min_length and len(value) < self.min_length:
            raise ValidationError(f"{self.field_name} must be at least {self.min_length} characters", self.field_name)
        
        if self.max_length and len(value) > self.max_length:
            raise ValidationError(f"{self.field_name} must be no more than {self.max_length} characters", self.field_name)
        
        if self.pattern and not re.match(self.pattern, value):
            raise ValidationError(f"{self.field_name} format is invalid", self.field_name)
        
        return value

class EmailValidator(StringValidator):
    """Validates email addresses."""
    
    def __init__(self, field_name: str = "email", required: bool = True):
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        super().__init__(field_name, pattern=email_pattern, required=required)

class PasswordValidator(StringValidator):
    """Validates passwords."""
    
    def __init__(self, field_name: str = "password", min_length: int = 6, required: bool = True):
        super().__init__(field_name, min_length=min_length, required=required)
    
    def _validate(self, value: str) -> str:
        value = super()._validate(value)
        
        # Additional password strength checks can be added here
        if len(value) < self.min_length:
            raise ValidationError(f"Password must be at least {self.min_length} characters", self.field_name)
        
        return value

class IntegerValidator(Validator):
    """Validates integer fields."""
    
    def __init__(self, field_name: str, min_value: int = None, max_value: int = None, required: bool = True):
        super().__init__(field_name, required)
        self.min_value = min_value
        self.max_value = max_value
    
    def _validate(self, value: Any) -> int:
        try:
            int_value = int(value)
        except (ValueError, TypeError):
            raise ValidationError(f"{self.field_name} must be a valid number", self.field_name)
        
        if self.min_value is not None and int_value < self.min_value:
            raise ValidationError(f"{self.field_name} must be at least {self.min_value}", self.field_name)
        
        if self.max_value is not None and int_value > self.max_value:
            raise ValidationError(f"{self.field_name} must be no more than {self.max_value}", self.field_name)
        
        return int_value

class FloatValidator(Validator):
    """Validates float fields."""
    
    def __init__(self, field_name: str, min_value: float = None, max_value: float = None, required: bool = True):
        super().__init__(field_name, required)
        self.min_value = min_value
        self.max_value = max_value
    
    def _validate(self, value: Any) -> float:
        try:
            float_value = float(value)
        except (ValueError, TypeError):
            raise ValidationError(f"{self.field_name} must be a valid number", self.field_name)
        
        if self.min_value is not None and float_value < self.min_value:
            raise ValidationError(f"{self.field_name} must be at least {self.min_value}", self.field_name)
        
        if self.max_value is not None and float_value > self.max_value:
            raise ValidationError(f"{self.field_name} must be no more than {self.max_value}", self.field_name)
        
        return float_value

class ChoiceValidator(Validator):
    """Validates choice fields."""
    
    def __init__(self, field_name: str, choices: List[Any], required: bool = True):
        super().__init__(field_name, required)
        self.choices = choices
    
    def _validate(self, value: Any) -> Any:
        if value not in self.choices:
            choices_str = ", ".join(str(choice) for choice in self.choices)
            raise ValidationError(f"{self.field_name} must be one of: {choices_str}", self.field_name)
        return value

def validate_form(validators: Dict[str, Validator]):
    """
    Decorator to validate form data.
    
    Args:
        validators: Dictionary mapping field names to validators
    
    Returns:
        Decorated function that validates form data before execution
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.method == "POST":
                try:
                    # Validate all fields
                    validated_data = {}
                    for field_name, validator in validators.items():
                        value = request.form.get(field_name)
                        validated_data[field_name] = validator.validate(value)
                    
                    # Add validated data to request
                    request.validated_data = validated_data
                    
                except ValidationError as e:
                    flash(e.message, "error")
                    return redirect(request.url)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def sanitize_input(value: str) -> str:
    """Sanitize string input to prevent XSS."""
    if not isinstance(value, str):
        return str(value)
    
    # Basic HTML entity encoding
    value = value.replace("&", "&amp;")
    value = value.replace("<", "&lt;")
    value = value.replace(">", "&gt;")
    value = value.replace('"', "&quot;")
    value = value.replace("'", "&#x27;")
    
    return value

def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> None:
    """Validate that required fields are present and not empty."""
    for field in required_fields:
        if field not in data or not data[field]:
            raise ValidationError(f"{field} is required", field)

def validate_email_format(email: str) -> bool:
    """Validate email format."""
    email_validator = EmailValidator("email")
    try:
        email_validator.validate(email)
        return True
    except ValidationError:
        return False

def validate_password_strength(password: str, min_length: int = 6) -> bool:
    """Validate password strength."""
    password_validator = PasswordValidator("password", min_length=min_length)
    try:
        password_validator.validate(password)
        return True
    except ValidationError:
        return False 