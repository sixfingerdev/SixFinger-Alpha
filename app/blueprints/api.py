from flask import Blueprint, jsonify, request, current_app
from functools import wraps
from app.models import db, APIKey, User, APIUsage
from datetime import datetime
import time
from autonomous_agent import AutonomousAgent

api_bp = Blueprint('api', __name__)

def require_api_key(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        
        if not api_key:
            return jsonify({
                'error': 'API key required',
                'message': 'Please provide an API key in the X-API-Key header or api_key parameter'
            }), 401
        
        key = APIKey.query.filter_by(key=api_key, is_active=True).first()
        
        if not key:
            return jsonify({
                'error': 'Invalid API key',
                'message': 'The provided API key is invalid or has been deactivated'
            }), 401
        
        user = User.query.get(key.user_id)
        
        if not user or not user.is_active:
            return jsonify({
                'error': 'Account inactive',
                'message': 'Your account has been deactivated'
            }), 403
        
        # Check rate limits
        if not user.can_make_request():
            plan = user.get_plan()
            limits = current_app.config['API_RATE_LIMITS'].get(plan, {})
            return jsonify({
                'error': 'Rate limit exceeded',
                'message': f'You have exceeded your {plan} plan limits',
                'limits': limits
            }), 429
        
        # Update last used timestamp
        key.last_used = datetime.utcnow()
        
        # Store in request context
        request.api_key = key
        request.api_user = user
        
        return f(*args, **kwargs)
    
    return decorated_function

def log_api_usage(endpoint, method, status_code, response_time):
    """Log API usage"""
    if hasattr(request, 'api_key') and hasattr(request, 'api_user'):
        usage = APIUsage(
            user_id=request.api_user.id,
            api_key_id=request.api_key.id,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time=response_time
        )
        db.session.add(usage)
        db.session.commit()

@api_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@api_bp.route('/query', methods=['POST'])
@require_api_key
def query():
    """Main AI query endpoint"""
    start_time = time.time()
    
    data = request.get_json()
    
    if not data or 'prompt' not in data:
        response_time = time.time() - start_time
        log_api_usage('/api/v1/query', 'POST', 400, response_time)
        return jsonify({
            'error': 'Missing prompt',
            'message': 'Please provide a prompt in the request body'
        }), 400
    
    prompt = data['prompt']
    stream = data.get('stream', False)
    
    try:
        agent = AutonomousAgent()
        
        # For API, we don't want streaming output to console
        # We'll modify the query to not stream
        response = agent.query(prompt, stream=False)
        
        response_time = time.time() - start_time
        log_api_usage('/api/v1/query', 'POST', 200, response_time)
        
        return jsonify({
            'success': True,
            'response': response,
            'usage': {
                'user': request.api_user.username,
                'plan': request.api_user.get_plan(),
                'response_time': response_time
            }
        }), 200
    
    except Exception as e:
        response_time = time.time() - start_time
        log_api_usage('/api/v1/query', 'POST', 500, response_time)
        return jsonify({
            'error': 'Internal error',
            'message': str(e)
        }), 500

@api_bp.route('/research', methods=['POST'])
@require_api_key
def research():
    """Research endpoint"""
    start_time = time.time()
    
    data = request.get_json()
    
    if not data or 'topic' not in data:
        response_time = time.time() - start_time
        log_api_usage('/api/v1/research', 'POST', 400, response_time)
        return jsonify({
            'error': 'Missing topic',
            'message': 'Please provide a topic in the request body'
        }), 400
    
    try:
        agent = AutonomousAgent()
        response = agent.query(
            f"Research and provide comprehensive information about: {data['topic']}",
            stream=False
        )
        
        response_time = time.time() - start_time
        log_api_usage('/api/v1/research', 'POST', 200, response_time)
        
        return jsonify({
            'success': True,
            'topic': data['topic'],
            'response': response,
            'response_time': response_time
        }), 200
    
    except Exception as e:
        response_time = time.time() - start_time
        log_api_usage('/api/v1/research', 'POST', 500, response_time)
        return jsonify({
            'error': 'Internal error',
            'message': str(e)
        }), 500

@api_bp.route('/code', methods=['POST'])
@require_api_key
def generate_code():
    """Code generation endpoint"""
    start_time = time.time()
    
    data = request.get_json()
    
    if not data or 'requirements' not in data:
        response_time = time.time() - start_time
        log_api_usage('/api/v1/code', 'POST', 400, response_time)
        return jsonify({
            'error': 'Missing requirements',
            'message': 'Please provide requirements in the request body'
        }), 400
    
    try:
        agent = AutonomousAgent()
        response = agent.query(
            f"Generate code for the following requirements: {data['requirements']}",
            stream=False
        )
        
        response_time = time.time() - start_time
        log_api_usage('/api/v1/code', 'POST', 200, response_time)
        
        return jsonify({
            'success': True,
            'requirements': data['requirements'],
            'response': response,
            'response_time': response_time
        }), 200
    
    except Exception as e:
        response_time = time.time() - start_time
        log_api_usage('/api/v1/code', 'POST', 500, response_time)
        return jsonify({
            'error': 'Internal error',
            'message': str(e)
        }), 500

@api_bp.route('/analyze', methods=['POST'])
@require_api_key
def analyze():
    """Analysis endpoint"""
    start_time = time.time()
    
    data = request.get_json()
    
    if not data or 'content' not in data:
        response_time = time.time() - start_time
        log_api_usage('/api/v1/analyze', 'POST', 400, response_time)
        return jsonify({
            'error': 'Missing content',
            'message': 'Please provide content to analyze in the request body'
        }), 400
    
    try:
        agent = AutonomousAgent()
        response = agent.query(
            f"Analyze the following content:\n\n{data['content']}",
            stream=False
        )
        
        response_time = time.time() - start_time
        log_api_usage('/api/v1/analyze', 'POST', 200, response_time)
        
        return jsonify({
            'success': True,
            'response': response,
            'response_time': response_time
        }), 200
    
    except Exception as e:
        response_time = time.time() - start_time
        log_api_usage('/api/v1/analyze', 'POST', 500, response_time)
        return jsonify({
            'error': 'Internal error',
            'message': str(e)
        }), 500

@api_bp.route('/usage', methods=['GET'])
@require_api_key
def get_usage():
    """Get API usage statistics for the authenticated user"""
    from sqlalchemy import func
    from datetime import timedelta
    
    # Get today's usage
    today = datetime.utcnow().date()
    daily_usage = APIUsage.query.filter(
        APIUsage.user_id == request.api_user.id,
        func.date(APIUsage.timestamp) == today
    ).count()
    
    # Get monthly usage
    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_usage = APIUsage.query.filter(
        APIUsage.user_id == request.api_user.id,
        APIUsage.timestamp >= month_start
    ).count()
    
    # Get plan limits
    plan = request.api_user.get_plan()
    limits = current_app.config['API_RATE_LIMITS'].get(plan, {})
    
    return jsonify({
        'user': request.api_user.username,
        'plan': plan,
        'usage': {
            'daily': daily_usage,
            'monthly': monthly_usage
        },
        'limits': limits,
        'remaining': {
            'daily': max(0, limits.get('daily', 0) - daily_usage) if limits.get('daily', 0) != -1 else 'unlimited',
            'monthly': max(0, limits.get('monthly', 0) - monthly_usage) if limits.get('monthly', 0) != -1 else 'unlimited'
        }
    }), 200

@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Not found',
        'message': 'The requested endpoint does not exist'
    }), 404

@api_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500
