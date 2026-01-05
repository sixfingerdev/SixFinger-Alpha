from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import string

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    email_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    subscription = db.relationship('Subscription', backref='user', uselist=False, cascade='all, delete-orphan')
    api_keys = db.relationship('APIKey', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    api_usage = db.relationship('APIUsage', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_plan(self):
        """Get user's subscription plan"""
        if self.subscription and self.subscription.is_active:
            return self.subscription.plan
        return 'free'
    
    def can_make_request(self):
        """Check if user can make API request based on their plan limits"""
        plan = self.get_plan()
        from flask import current_app
        limits = current_app.config['API_RATE_LIMITS'].get(plan, {})
        
        daily_limit = limits.get('daily', 0)
        monthly_limit = limits.get('monthly', 0)
        
        if daily_limit == -1:  # Unlimited
            return True
        
        # Check daily usage
        today = datetime.utcnow().date()
        daily_usage = APIUsage.query.filter(
            APIUsage.user_id == self.id,
            db.func.date(APIUsage.timestamp) == today
        ).count()
        
        if daily_usage >= daily_limit:
            return False
        
        # Check monthly usage
        month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_usage = APIUsage.query.filter(
            APIUsage.user_id == self.id,
            APIUsage.timestamp >= month_start
        ).count()
        
        return monthly_usage < monthly_limit
    
    def __repr__(self):
        return f'<User {self.username}>'


class Subscription(db.Model):
    """Subscription model"""
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    plan = db.Column(db.String(50), nullable=False, default='free')
    currency = db.Column(db.String(3), nullable=False, default='USD')
    is_active = db.Column(db.Boolean, default=True)
    stripe_customer_id = db.Column(db.String(255))
    stripe_subscription_id = db.Column(db.String(255))
    current_period_start = db.Column(db.DateTime)
    current_period_end = db.Column(db.DateTime)
    cancel_at_period_end = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def is_expired(self):
        """Check if subscription is expired"""
        if not self.current_period_end:
            return False
        return datetime.utcnow() > self.current_period_end
    
    def days_remaining(self):
        """Get days remaining in current period"""
        if not self.current_period_end:
            return None
        delta = self.current_period_end - datetime.utcnow()
        return max(0, delta.days)
    
    def __repr__(self):
        return f'<Subscription {self.plan} for user {self.user_id}>'


class APIKey(db.Model):
    """API Key model for developer portal"""
    __tablename__ = 'api_keys'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    key = db.Column(db.String(64), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used = db.Column(db.DateTime)
    
    @staticmethod
    def generate_key():
        """Generate a secure API key"""
        alphabet = string.ascii_letters + string.digits
        return 'sk_' + ''.join(secrets.choice(alphabet) for _ in range(48))
    
    def __repr__(self):
        return f'<APIKey {self.name}>'


class APIUsage(db.Model):
    """API Usage tracking model"""
    __tablename__ = 'api_usage'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    api_key_id = db.Column(db.Integer, db.ForeignKey('api_keys.id'))
    endpoint = db.Column(db.String(255))
    method = db.Column(db.String(10))
    status_code = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    response_time = db.Column(db.Float)
    
    def __repr__(self):
        return f'<APIUsage {self.endpoint} at {self.timestamp}>'


class EmailVerification(db.Model):
    """Email verification tokens"""
    __tablename__ = 'email_verifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @staticmethod
    def generate_token():
        """Generate a secure verification token"""
        return secrets.token_urlsafe(32)
    
    def is_expired(self):
        """Check if token is expired"""
        return datetime.utcnow() > self.expires_at
    
    def __repr__(self):
        return f'<EmailVerification for user {self.user_id}>'
