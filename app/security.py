"""
Security utilities and helpers
"""
import re
from functools import wraps
from flask import request, jsonify, abort
from flask_login import current_user

def sanitize_input(text):
    """
    Sanitize user input to prevent XSS attacks
    """
    if not text:
        return text
    
    # Remove potentially dangerous characters/patterns
    text = str(text).strip()
    
    # Remove HTML tags
    text = re.sub(r'<[^>]*>', '', text)
    
    # Remove script tags
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    return text

def validate_email(email):
    """
    Validate email format
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_safe_url(target):
    """
    Check if URL is safe for redirects
    """
    from urllib.parse import urlparse, urljoin
    from flask import request
    
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

def check_password_strength(password):
    """
    Check password strength
    Returns (is_strong, message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    # Check for common weak passwords
    weak_passwords = [
        'password', 'password123', '12345678', 'qwerty', 
        'abc123', 'monkey', '1234567890', 'letmein'
    ]
    
    if password.lower() in weak_passwords:
        return False, "Password is too common"
    
    return True, "Strong password"

def admin_required(f):
    """
    Decorator to require admin access
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def validate_api_request(required_fields):
    """
    Decorator to validate API request JSON data
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'error': 'Invalid request',
                    'message': 'Request body must be JSON'
                }), 400
            
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                return jsonify({
                    'error': 'Missing required fields',
                    'fields': missing_fields
                }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def log_security_event(event_type, details, user_id=None):
    """
    Log security-related events
    """
    from datetime import datetime
    import logging
    
    logger = logging.getLogger('security')
    
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'event_type': event_type,
        'details': details,
        'user_id': user_id,
        'ip': request.remote_addr if request else None,
        'user_agent': request.user_agent.string if request else None
    }
    
    logger.warning(f"Security Event: {log_entry}")

def rate_limit_key():
    """
    Generate rate limit key based on user or IP
    """
    if current_user.is_authenticated:
        return f"user:{current_user.id}"
    return f"ip:{request.remote_addr}"
