from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models import db, APIKey, APIUsage
from datetime import datetime, timedelta
from sqlalchemy import func

developer_bp = Blueprint('developer', __name__)

@developer_bp.route('/')
@login_required
def portal():
    """Developer portal home"""
    api_keys = APIKey.query.filter_by(user_id=current_user.id).all()
    
    # Get usage statistics
    today = datetime.utcnow().date()
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    daily_stats = db.session.query(
        func.date(APIUsage.timestamp).label('date'),
        func.count(APIUsage.id).label('count')
    ).filter(
        APIUsage.user_id == current_user.id,
        APIUsage.timestamp >= week_ago
    ).group_by(func.date(APIUsage.timestamp)).all()
    
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
    existing_keys = APIKey.query.filter_by(user_id=current_user.id, is_active=True).count()
    max_keys = 10
    
    if existing_keys >= max_keys:
        flash(f'You can only have up to {max_keys} active API keys', 'error')
        return redirect(url_for('developer.portal'))
    
    # Create API key
    api_key = APIKey(
        user_id=current_user.id,
        key=APIKey.generate_key(),
        name=name
    )
    db.session.add(api_key)
    db.session.commit()
    
    flash(f'API key created successfully: {api_key.key}', 'success')
    flash('Make sure to copy your API key now. You will not be able to see it again!', 'warning')
    return redirect(url_for('developer.portal'))

@developer_bp.route('/api-keys/<int:key_id>/delete', methods=['POST'])
@login_required
def delete_api_key(key_id):
    """Delete an API key"""
    api_key = APIKey.query.filter_by(id=key_id, user_id=current_user.id).first()
    
    if not api_key:
        flash('API key not found', 'error')
        return redirect(url_for('developer.portal'))
    
    db.session.delete(api_key)
    db.session.commit()
    
    flash('API key deleted successfully', 'success')
    return redirect(url_for('developer.portal'))

@developer_bp.route('/api-keys/<int:key_id>/toggle', methods=['POST'])
@login_required
def toggle_api_key(key_id):
    """Toggle API key active status"""
    api_key = APIKey.query.filter_by(id=key_id, user_id=current_user.id).first()
    
    if not api_key:
        flash('API key not found', 'error')
        return redirect(url_for('developer.portal'))
    
    api_key.is_active = not api_key.is_active
    db.session.commit()
    
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
    usage_data = APIUsage.query.filter(
        APIUsage.user_id == current_user.id,
        APIUsage.timestamp >= start_date
    ).order_by(APIUsage.timestamp.desc()).limit(1000).all()
    
    # Group by endpoint
    endpoint_stats = db.session.query(
        APIUsage.endpoint,
        func.count(APIUsage.id).label('count'),
        func.avg(APIUsage.response_time).label('avg_response_time')
    ).filter(
        APIUsage.user_id == current_user.id,
        APIUsage.timestamp >= start_date
    ).group_by(APIUsage.endpoint).all()
    
    return render_template('developer/usage.html',
                         usage_data=usage_data,
                         endpoint_stats=endpoint_stats,
                         days=days)
