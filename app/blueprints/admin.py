from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from app.models import User, Subscription, APIKey, APIUsage
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
    total_users = User.count()
    active_users = User.count_active()
    verified_users = User.count_verified()
    
    # Subscription statistics
    subscription_stats = Subscription.get_plan_stats()
    
    # API usage today
    api_requests_today = APIUsage.count_today()
    
    # Recent users
    recent_users = sorted(User.get_all_users(), key=lambda u: u.created_at, reverse=True)[:10]
    
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
    all_users = User.get_all_users()
    
    if search:
        all_users = [u for u in all_users 
                    if search.lower() in u.username.lower() or search.lower() in u.email.lower()]
    
    # Sort by created_at desc
    all_users.sort(key=lambda u: u.created_at, reverse=True)
    
    # Simple pagination
    total = len(all_users)
    start = (page - 1) * per_page
    end = start + per_page
    users_page = all_users[start:end]
    
    # Create pagination object
    class Pagination:
        def __init__(self, items, page, per_page, total):
            self.items = items
            self.page = page
            self.per_page = per_page
            self.total = total
            self.pages = (total + per_page - 1) // per_page
            self.has_prev = page > 1
            self.has_next = page < self.pages
            self.prev_num = page - 1 if self.has_prev else None
            self.next_num = page + 1 if self.has_next else None
    
    pagination = Pagination(users_page, page, per_page, total)
    
    return render_template('admin/users.html',
                         users=pagination.items,
                         pagination=pagination,
                         search=search)

@admin_bp.route('/users/<int:user_id>')
@login_required
@admin_required
def user_detail(user_id):
    """View user details"""
    user = User.query_by_id(user_id)
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('admin.users'))
    
    # Get user's API keys
    api_keys = APIKey.query_by_user_id(user_id)
    
    # Get usage statistics
    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_usage = len(APIUsage.query_by_user_id(user_id, start_date=month_start))
    
    return render_template('admin/user_detail.html',
                         user=user,
                         api_keys=api_keys,
                         monthly_usage=monthly_usage)

@admin_bp.route('/users/<int:user_id>/toggle-active', methods=['POST'])
@login_required
@admin_required
def toggle_user_active(user_id):
    """Toggle user active status"""
    user = User.query_by_id(user_id)
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('admin.users'))
    
    if user.id == current_user.id:
        flash('You cannot deactivate your own account', 'error')
        return redirect(url_for('admin.user_detail', user_id=user_id))
    
    user.is_active = not user.is_active
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {status} successfully', 'success')
    return redirect(url_for('admin.user_detail', user_id=user_id))

@admin_bp.route('/users/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def toggle_user_admin(user_id):
    """Toggle user admin status"""
    user = User.query_by_id(user_id)
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('admin.users'))
    
    if user.id == current_user.id:
        flash('You cannot modify your own admin status', 'error')
        return redirect(url_for('admin.user_detail', user_id=user_id))
    
    user.is_admin = not user.is_admin
    
    status = 'granted' if user.is_admin else 'revoked'
    flash(f'Admin privileges {status} successfully', 'success')
    return redirect(url_for('admin.user_detail', user_id=user_id))

@admin_bp.route('/users/<int:user_id>/change-plan', methods=['POST'])
@login_required
@admin_required
def change_user_plan(user_id):
    """Change user's subscription plan"""
    user = User.query_by_id(user_id)
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('admin.users'))
    
    plan = request.form.get('plan')
    
    from flask import current_app
    if plan not in current_app.config['SUBSCRIPTION_PLANS']:
        flash('Invalid plan selected', 'error')
        return redirect(url_for('admin.user_detail', user_id=user_id))
    
    if not user.subscription:
        subscription = Subscription(user_id=user_id, plan=plan)
    else:
        user.subscription.plan = plan
    
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
    from collections import defaultdict
    daily_reg = defaultdict(int)
    for user in User.get_all_users():
        if user.created_at >= start_date:
            date = user.created_at.date()
            daily_reg[date] += 1
    daily_registrations = [(date, count) for date, count in sorted(daily_reg.items())]
    
    # Daily API usage
    daily_api_usage = APIUsage.get_daily_stats(start_date)
    
    # Top users by API usage
    top_users = APIUsage.get_top_users(start_date, limit=10)
    
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
