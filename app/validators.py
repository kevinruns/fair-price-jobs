"""
Input validation utilities for the Jobeco application.

This module provides validation functions and classes for form inputs.
"""

import re
from typing import Optional, Dict, Any, List
from app.exceptions import ValidationError


def validate_form(data: Dict[str, Any], validators: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate form data against specified validators.
    
    Args:
        data: Form data to validate
        validators: Dictionary of field names and their validators
        
    Returns:
        Validated data
        
    Raises:
        ValidationError: If validation fails
    """
    validated_data = {}
    errors = {}
    
    for field, validator in validators.items():
        try:
            value = data.get(field, '')
            validated_value = validator.validate(value)
            validated_data[field] = validated_value
        except ValidationError as e:
            errors[field] = e.message
    
    if errors:
        raise ValidationError("Validation failed", errors=errors)
    
    return validated_data


class StringValidator:
    """Validator for string fields."""
    
    def __init__(self, min_length: int = 0, max_length: int = None, required: bool = True):
        self.min_length = min_length
        self.max_length = max_length
        self.required = required
    
    def validate(self, value: str) -> str:
        """Validate a string value."""
        if not value and self.required:
            raise ValidationError("This field is required")
        
        if value:
            if len(value) < self.min_length:
                raise ValidationError(f"Minimum length is {self.min_length} characters")
            
            if self.max_length and len(value) > self.max_length:
                raise ValidationError(f"Maximum length is {self.max_length} characters")
        
        return value.strip() if value else value


class EmailValidator:
    """Validator for email fields."""
    
    def __init__(self, required: bool = True):
        self.required = required
        self.email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    def validate(self, value: str) -> str:
        """Validate an email value."""
        if not value and self.required:
            raise ValidationError("Email is required")
        
        if value:
            value = value.strip().lower()
            if not self.email_pattern.match(value):
                raise ValidationError("Invalid email format")
        
        return value


class PasswordValidator:
    """Validator for password fields."""
    
    def __init__(self, min_length: int = 6, require_special: bool = False):
        self.min_length = min_length
        self.require_special = require_special
    
    def validate(self, value: str) -> str:
        """Validate a password value."""
        if not value:
            raise ValidationError("Password is required")
        
        if len(value) < self.min_length:
            raise ValidationError(f"Password must be at least {self.min_length} characters")
        
        if self.require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValidationError("Password must contain at least one special character")
        
        return value


class NumberValidator:
    """Validator for numeric fields."""
    
    def __init__(self, min_value: float = None, max_value: float = None, required: bool = True):
        self.min_value = min_value
        self.max_value = max_value
        self.required = required
    
    def validate(self, value: str) -> float:
        """Validate a numeric value."""
        if not value and self.required:
            raise ValidationError("This field is required")
        
        if value:
            try:
                num_value = float(value)
                
                if self.min_value is not None and num_value < self.min_value:
                    raise ValidationError(f"Value must be at least {self.min_value}")
                
                if self.max_value is not None and num_value > self.max_value:
                    raise ValidationError(f"Value must be at most {self.max_value}")
                
                return num_value
            except ValueError:
                raise ValidationError("Invalid number format")
        
        return None