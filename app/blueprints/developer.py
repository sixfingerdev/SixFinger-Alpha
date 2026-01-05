from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models import APIKey, APIUsage
from datetime import datetime, timedelta

developer_bp = Blueprint('developer', __name__)

@developer_bp.route('/')
@login_required
def portal():
    """Developer portal home"""
    api_keys = APIKey.query_by_user_id(current_user.id)
    
    # Get usage statistics
    today = datetime.utcnow().date()
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    # Calculate daily stats
    from collections import defaultdict
    daily_counts = defaultdict(int)
    for usage in APIUsage.query_by_user_id(current_user.id, start_date=week_ago):
        date = usage.timestamp.date()
        daily_counts[date] += 1
    
    daily_stats = [(date, count) for date, count in sorted(daily_counts.items())]
    
    return render_template('developer/portal.html',
                         api_keys=api_keys,
                         daily_stats=daily_stats)

@developer_bp.route('/api-keys/create', methods=['POST'])
@login_required
def create_api_key():
    """Create a new API key"""
    name = request.form.get('name', '').strip()
    
    if not name:
        flash('API key name is required', 'error')
        return redirect(url_for('developer.portal'))
    
    # Check if user has reached the limit
    existing_keys = len(APIKey.query_by_user_id(current_user.id, active_only=True))
    max_keys = 10
    
    if existing_keys >= max_keys:
        flash(f'You can only have up to {max_keys} active API keys', 'error')
        return redirect(url_for('developer.portal'))
    
    # Create API key
    try:
        api_key = APIKey(
            user_id=current_user.id,
            key=APIKey.generate_key(),
            name=name
        )
        
        flash(f'API key created successfully: {api_key.key}', 'success')
        flash('Make sure to copy your API key now. You will not be able to see it again!', 'warning')
    except ValueError as e:
        flash(str(e), 'error')
    
    return redirect(url_for('developer.portal'))

@developer_bp.route('/api-keys/<int:key_id>/delete', methods=['POST'])
@login_required
def delete_api_key(key_id):
    """Delete an API key"""
    api_key = APIKey.query_by_id(key_id)
    
    if not api_key or api_key.user_id != current_user.id:
        flash('API key not found', 'error')
        return redirect(url_for('developer.portal'))
    
    APIKey.delete(key_id)
    
    flash('API key deleted successfully', 'success')
    return redirect(url_for('developer.portal'))

@developer_bp.route('/api-keys/<int:key_id>/toggle', methods=['POST'])
@login_required
def toggle_api_key(key_id):
    """Toggle API key active status"""
    api_key = APIKey.query_by_id(key_id)
    
    if not api_key or api_key.user_id != current_user.id:
        flash('API key not found', 'error')
        return redirect(url_for('developer.portal'))
    
    api_key.is_active = not api_key.is_active
    
    status = 'activated' if api_key.is_active else 'deactivated'
    flash(f'API key {status} successfully', 'success')
    return redirect(url_for('developer.portal'))

@developer_bp.route('/usage')
@login_required
def usage():
    """View API usage details"""
    # Get date range from query params
    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get usage data
    usage_data = APIUsage.query_by_user_id(current_user.id, start_date=start_date, limit=1000)
    
    # Group by endpoint
    endpoint_stats = APIUsage.get_endpoint_stats(current_user.id, start_date)
    
    return render_template('developer/usage.html',
                         usage_data=usage_data,
                         endpoint_stats=endpoint_stats,
                         days=days)
