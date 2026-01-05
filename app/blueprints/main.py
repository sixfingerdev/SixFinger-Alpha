from flask import Blueprint, render_template, current_app
from flask_login import login_required, current_user
from app.models import APIUsage, APIKey
from datetime import datetime
from sqlalchemy import func

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
