from flask import Blueprint, render_template, current_app, request, jsonify
from flask_login import login_required, current_user
from app.models import APIUsage, APIKey
from datetime import datetime
from sqlalchemy import func
from autonomous_agent import AutonomousAgent
import time

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Homepage"""
    plans = current_app.config['SUBSCRIPTION_PLANS']
    return render_template('index.html', plans=plans)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    # Get API usage statistics
    today = datetime.utcnow().date()
    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    daily_usage = APIUsage.query.filter(
        APIUsage.user_id == current_user.id,
        func.date(APIUsage.timestamp) == today
    ).count()
    
    monthly_usage = APIUsage.query.filter(
        APIUsage.user_id == current_user.id,
        APIUsage.timestamp >= month_start
    ).count()
    
    # Get user's plan and limits
    plan = current_user.get_plan()
    limits = current_app.config['API_RATE_LIMITS'].get(plan, {})
    
    # Get API keys count
    api_keys_count = APIKey.query.filter_by(user_id=current_user.id, is_active=True).count()
    
    return render_template('dashboard.html',
                         daily_usage=daily_usage,
                         monthly_usage=monthly_usage,
                         limits=limits,
                         plan=plan,
                         api_keys_count=api_keys_count)

@main_bp.route('/pricing')
def pricing():
    """Pricing page"""
    plans = current_app.config['SUBSCRIPTION_PLANS']
    currency = 'USD'  # Default, can be changed based on user preference
    return render_template('pricing.html', plans=plans, currency=currency)

@main_bp.route('/docs')
def documentation():
    """API documentation"""
    return render_template('docs.html')

@main_bp.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@main_bp.route('/contact')
def contact():
    """Contact page"""
    return render_template('contact.html')

@main_bp.route('/playground')
@login_required
def playground():
    """AI Playground - Interactive AI interface"""
    return render_template('playground.html')

@main_bp.route('/playground/query', methods=['POST'])
@login_required
def playground_query():
    """Handle AI queries from the playground"""
    from app.models import db
    
    # Check rate limits
    if not current_user.can_make_request():
        return jsonify({
            'success': False,
            'error': 'Rate limit exceeded. Please upgrade your plan.'
        }), 429
    
    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({
            'success': False,
            'error': 'Missing prompt'
        }), 400
    
    prompt = data['prompt']
    mode = data.get('mode', 'general')  # general, research, code, article, websearch, agent
    
    try:
        agent = AutonomousAgent()
        
        # Customize prompt based on mode
        if mode == 'research':
            enhanced_prompt = f"Research and provide comprehensive information about: {prompt}"
        elif mode == 'code':
            enhanced_prompt = f"Generate code for the following requirements: {prompt}"
        elif mode == 'article':
            enhanced_prompt = f"Write a detailed, well-structured article about: {prompt}"
        elif mode == 'websearch':
            enhanced_prompt = f"Perform a web search and summarize information about: {prompt}"
        elif mode == 'agent':
            enhanced_prompt = f"As an autonomous agent, analyze and execute this task: {prompt}"
        else:
            enhanced_prompt = prompt
        
        start_time = time.time()
        response = agent.query(enhanced_prompt, stream=False)
        response_time = time.time() - start_time
        
        # Log usage
        usage = APIUsage(
            user_id=current_user.id,
            api_key_id=None,
            endpoint='/playground/query',
            method='POST',
            status_code=200,
            response_time=response_time
        )
        db.session.add(usage)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'response': response,
            'mode': mode,
            'response_time': round(response_time, 2)
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
