from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from app.models import db, User, Subscription, APIKey, APIUsage
from sqlalchemy import func
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You do not have permission to access this page', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    """Admin dashboard"""
    # Get statistics
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    verified_users = User.query.filter_by(email_verified=True).count()
    
    # Subscription statistics
    subscription_stats = db.session.query(
        Subscription.plan,
        func.count(Subscription.id).label('count')
    ).group_by(Subscription.plan).all()
    
    # API usage today
    today = datetime.utcnow().date()
    api_requests_today = APIUsage.query.filter(
        func.date(APIUsage.timestamp) == today
    ).count()
    
    # Recent users
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         active_users=active_users,
                         verified_users=verified_users,
                         subscription_stats=subscription_stats,
                         api_requests_today=api_requests_today,
                         recent_users=recent_users)

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """View all users"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    search = request.args.get('search', '')
    query = User.query
    
    if search:
        query = query.filter(
            (User.username.contains(search)) |
            (User.email.contains(search))
        )
    
    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/users.html',
                         users=pagination.items,
                         pagination=pagination,
                         search=search)

@admin_bp.route('/users/<int:user_id>')
@login_required
@admin_required
def user_detail(user_id):
    """View user details"""
    user = User.query.get_or_404(user_id)
    
    # Get user's API keys
    api_keys = APIKey.query.filter_by(user_id=user_id).all()
    
    # Get usage statistics
    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_usage = APIUsage.query.filter(
        APIUsage.user_id == user_id,
        APIUsage.timestamp >= month_start
    ).count()
    
    return render_template('admin/user_detail.html',
                         user=user,
                         api_keys=api_keys,
                         monthly_usage=monthly_usage)

@admin_bp.route('/users/<int:user_id>/toggle-active', methods=['POST'])
@login_required
@admin_required
def toggle_user_active(user_id):
    """Toggle user active status"""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('You cannot deactivate your own account', 'error')
        return redirect(url_for('admin.user_detail', user_id=user_id))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {status} successfully', 'success')
    return redirect(url_for('admin.user_detail', user_id=user_id))

@admin_bp.route('/users/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def toggle_user_admin(user_id):
    """Toggle user admin status"""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('You cannot modify your own admin status', 'error')
        return redirect(url_for('admin.user_detail', user_id=user_id))
    
    user.is_admin = not user.is_admin
    db.session.commit()
    
    status = 'granted' if user.is_admin else 'revoked'
    flash(f'Admin privileges {status} successfully', 'success')
    return redirect(url_for('admin.user_detail', user_id=user_id))

@admin_bp.route('/users/<int:user_id>/change-plan', methods=['POST'])
@login_required
@admin_required
def change_user_plan(user_id):
    """Change user's subscription plan"""
    user = User.query.get_or_404(user_id)
    plan = request.form.get('plan')
    
    from flask import current_app
    if plan not in current_app.config['SUBSCRIPTION_PLANS']:
        flash('Invalid plan selected', 'error')
        return redirect(url_for('admin.user_detail', user_id=user_id))
    
    if not user.subscription:
        subscription = Subscription(user_id=user_id, plan=plan)
        db.session.add(subscription)
    else:
        user.subscription.plan = plan
    
    db.session.commit()
    flash(f'User plan changed to {plan}', 'success')
    return redirect(url_for('admin.user_detail', user_id=user_id))

@admin_bp.route('/analytics')
@login_required
@admin_required
def analytics():
    """View system analytics"""
    # Get date range
    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Daily registrations
    daily_registrations = db.session.query(
        func.date(User.created_at).label('date'),
        func.count(User.id).label('count')
    ).filter(
        User.created_at >= start_date
    ).group_by(func.date(User.created_at)).all()
    
    # Daily API usage
    daily_api_usage = db.session.query(
        func.date(APIUsage.timestamp).label('date'),
        func.count(APIUsage.id).label('count')
    ).filter(
        APIUsage.timestamp >= start_date
    ).group_by(func.date(APIUsage.timestamp)).all()
    
    # Top users by API usage
    top_users = db.session.query(
        User.username,
        User.email,
        func.count(APIUsage.id).label('request_count')
    ).join(APIUsage).filter(
        APIUsage.timestamp >= start_date
    ).group_by(User.id).order_by(func.count(APIUsage.id).desc()).limit(10).all()
    
    return render_template('admin/analytics.html',
                         daily_registrations=daily_registrations,
                         daily_api_usage=daily_api_usage,
                         top_users=top_users,
                         days=days)

@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def settings():
    """Admin settings"""
    if request.method == 'POST':
        # Handle settings update
        flash('Settings updated successfully', 'success')
        return redirect(url_for('admin.settings'))
    
    return render_template('admin/settings.html')
