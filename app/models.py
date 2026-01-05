from datetime import datetime, timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import string

# In-memory storage
users_storage = {}  # {user_id: User}
users_by_email = {}  # {email: user_id}
users_by_username = {}  # {username: user_id}
subscriptions_storage = {}  # {user_id: Subscription}
api_keys_storage = {}  # {key_id: APIKey}
api_keys_by_key = {}  # {key: key_id}
api_usage_storage = []  # [APIUsage]
email_verifications_storage = {}  # {token: EmailVerification}

# Auto-increment IDs
_user_id_counter = [1]
_subscription_id_counter = [1]
_api_key_id_counter = [1]
_api_usage_id_counter = [1]
_email_verification_id_counter = [1]

class User(UserMixin):
    """User model"""
    
    def __init__(self, email, username, password_hash=None, is_active=True, is_admin=False, 
                 email_verified=False, created_at=None, last_login=None, id=None):
        if id is None:
            self.id = _user_id_counter[0]
            _user_id_counter[0] += 1
        else:
            self.id = id
            if id >= _user_id_counter[0]:
                _user_id_counter[0] = id + 1
        
        self.email = email.lower()
        self.username = username
        self.password_hash = password_hash or ''
        self.is_active = is_active
        self.is_admin = is_admin
        self.email_verified = email_verified
        self.created_at = created_at or datetime.utcnow()
        self.last_login = last_login
        
        # Store in memory
        users_storage[self.id] = self
        users_by_email[self.email] = self.id
        users_by_username[self.username] = self.id
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_plan(self):
        """Get user's subscription plan"""
        subscription = subscriptions_storage.get(self.id)
        if subscription and subscription.is_active:
            return subscription.plan
        return 'free'
    
    @property
    def subscription(self):
        """Get user's subscription"""
        return subscriptions_storage.get(self.id)
    
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
        daily_usage = sum(1 for usage in api_usage_storage 
                         if usage.user_id == self.id and usage.timestamp.date() == today)
        
        if daily_usage >= daily_limit:
            return False
        
        # Check monthly usage
        month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_usage = sum(1 for usage in api_usage_storage 
                           if usage.user_id == self.id and usage.timestamp >= month_start)
        
        return monthly_usage < monthly_limit
    
    @staticmethod
    def query_by_email(email):
        """Query user by email"""
        user_id = users_by_email.get(email.lower())
        return users_storage.get(user_id) if user_id else None
    
    @staticmethod
    def query_by_username(username):
        """Query user by username"""
        user_id = users_by_username.get(username)
        return users_storage.get(user_id) if user_id else None
    
    @staticmethod
    def query_by_id(user_id):
        """Query user by ID"""
        return users_storage.get(user_id)
    
    @staticmethod
    def get_all_users():
        """Get all users"""
        return list(users_storage.values())
    
    @staticmethod
    def count():
        """Count all users"""
        return len(users_storage)
    
    @staticmethod
    def count_active():
        """Count active users"""
        return sum(1 for user in users_storage.values() if user.is_active)
    
    @staticmethod
    def count_verified():
        """Count verified users"""
        return sum(1 for user in users_storage.values() if user.email_verified)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Subscription:
    """Subscription model"""
    
    def __init__(self, user_id, plan='free', currency='USD', is_active=True, 
                 stripe_customer_id=None, stripe_subscription_id=None,
                 current_period_start=None, current_period_end=None,
                 cancel_at_period_end=False, created_at=None, updated_at=None, id=None):
        if id is None:
            self.id = _subscription_id_counter[0]
            _subscription_id_counter[0] += 1
        else:
            self.id = id
            if id >= _subscription_id_counter[0]:
                _subscription_id_counter[0] = id + 1
        
        self.user_id = user_id
        self.plan = plan
        self.currency = currency
        self.is_active = is_active
        self.stripe_customer_id = stripe_customer_id
        self.stripe_subscription_id = stripe_subscription_id
        self.current_period_start = current_period_start
        self.current_period_end = current_period_end
        self.cancel_at_period_end = cancel_at_period_end
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        
        # Store in memory
        subscriptions_storage[user_id] = self
    
    @property
    def user(self):
        """Get user associated with subscription"""
        return users_storage.get(self.user_id)
    
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
    
    @staticmethod
    def query_by_user_id(user_id):
        """Query subscription by user ID"""
        return subscriptions_storage.get(user_id)
    
    @staticmethod
    def query_by_stripe_subscription_id(stripe_subscription_id):
        """Query subscription by Stripe subscription ID"""
        for subscription in subscriptions_storage.values():
            if subscription.stripe_subscription_id == stripe_subscription_id:
                return subscription
        return None
    
    @staticmethod
    def get_plan_stats():
        """Get subscription statistics by plan"""
        stats = {}
        for subscription in subscriptions_storage.values():
            plan = subscription.plan
            stats[plan] = stats.get(plan, 0) + 1
        return [(plan, count) for plan, count in stats.items()]
    
    def __repr__(self):
        return f'<Subscription {self.plan} for user {self.user_id}>'


class APIKey:
    """API Key model for developer portal"""
    
    def __init__(self, user_id, key, name, is_active=True, created_at=None, last_used=None, id=None):
        if id is None:
            self.id = _api_key_id_counter[0]
            _api_key_id_counter[0] += 1
        else:
            self.id = id
            if id >= _api_key_id_counter[0]:
                _api_key_id_counter[0] = id + 1
        
        self.user_id = user_id
        self.key = key
        self.name = name
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.last_used = last_used
        
        # Store in memory
        api_keys_storage[self.id] = self
        api_keys_by_key[key] = self.id
    
    @property
    def user(self):
        """Get user associated with API key"""
        return users_storage.get(self.user_id)
    
    @staticmethod
    def generate_key():
        """Generate a secure API key"""
        alphabet = string.ascii_letters + string.digits
        return 'sk_' + ''.join(secrets.choice(alphabet) for _ in range(48))
    
    @staticmethod
    def query_by_key(key):
        """Query API key by key value"""
        key_id = api_keys_by_key.get(key)
        return api_keys_storage.get(key_id) if key_id else None
    
    @staticmethod
    def query_by_user_id(user_id, active_only=False):
        """Query API keys by user ID"""
        keys = [key for key in api_keys_storage.values() if key.user_id == user_id]
        if active_only:
            keys = [key for key in keys if key.is_active]
        return keys
    
    @staticmethod
    def query_by_id(key_id):
        """Query API key by ID"""
        return api_keys_storage.get(key_id)
    
    @staticmethod
    def delete(key_id):
        """Delete an API key"""
        if key_id in api_keys_storage:
            key = api_keys_storage[key_id]
            del api_keys_by_key[key.key]
            del api_keys_storage[key_id]
            return True
        return False
    
    def __repr__(self):
        return f'<APIKey {self.name}>'


class APIUsage:
    """API Usage tracking model"""
    
    def __init__(self, user_id, api_key_id=None, endpoint=None, method=None, 
                 status_code=None, timestamp=None, response_time=None, id=None):
        if id is None:
            self.id = _api_usage_id_counter[0]
            _api_usage_id_counter[0] += 1
        else:
            self.id = id
            if id >= _api_usage_id_counter[0]:
                _api_usage_id_counter[0] = id + 1
        
        self.user_id = user_id
        self.api_key_id = api_key_id
        self.endpoint = endpoint
        self.method = method
        self.status_code = status_code
        self.timestamp = timestamp or datetime.utcnow()
        self.response_time = response_time
        
        # Store in memory
        api_usage_storage.append(self)
    
    @property
    def user(self):
        """Get user associated with usage"""
        return users_storage.get(self.user_id)
    
    @staticmethod
    def query_by_user_id(user_id, start_date=None, limit=None):
        """Query API usage by user ID"""
        usage = [u for u in api_usage_storage if u.user_id == user_id]
        if start_date:
            usage = [u for u in usage if u.timestamp >= start_date]
        usage.sort(key=lambda x: x.timestamp, reverse=True)
        if limit:
            usage = usage[:limit]
        return usage
    
    @staticmethod
    def count_by_date(user_id, date):
        """Count API usage for a specific date"""
        return sum(1 for u in api_usage_storage 
                  if u.user_id == user_id and u.timestamp.date() == date)
    
    @staticmethod
    def count_today():
        """Count total API usage today"""
        today = datetime.utcnow().date()
        return sum(1 for u in api_usage_storage if u.timestamp.date() == today)
    
    @staticmethod
    def get_daily_stats(start_date=None):
        """Get daily API usage statistics"""
        from collections import defaultdict
        stats = defaultdict(int)
        for usage in api_usage_storage:
            if start_date and usage.timestamp < start_date:
                continue
            date = usage.timestamp.date()
            stats[date] += 1
        return [(date, count) for date, count in sorted(stats.items())]
    
    @staticmethod
    def get_endpoint_stats(user_id, start_date=None):
        """Get endpoint statistics for a user"""
        from collections import defaultdict
        endpoint_counts = defaultdict(int)
        endpoint_times = defaultdict(list)
        
        for usage in api_usage_storage:
            if usage.user_id != user_id:
                continue
            if start_date and usage.timestamp < start_date:
                continue
            endpoint_counts[usage.endpoint] += 1
            if usage.response_time:
                endpoint_times[usage.endpoint].append(usage.response_time)
        
        stats = []
        for endpoint, count in endpoint_counts.items():
            avg_time = sum(endpoint_times[endpoint]) / len(endpoint_times[endpoint]) if endpoint_times[endpoint] else 0
            stats.append((endpoint, count, avg_time))
        return stats
    
    @staticmethod
    def get_top_users(start_date=None, limit=10):
        """Get top users by API usage"""
        from collections import defaultdict
        user_counts = defaultdict(int)
        
        for usage in api_usage_storage:
            if start_date and usage.timestamp < start_date:
                continue
            user_counts[usage.user_id] += 1
        
        top_users = []
        for user_id, count in sorted(user_counts.items(), key=lambda x: x[1], reverse=True)[:limit]:
            user = users_storage.get(user_id)
            if user:
                top_users.append((user.username, user.email, count))
        return top_users
    
    def __repr__(self):
        return f'<APIUsage {self.endpoint} at {self.timestamp}>'


class EmailVerification:
    """Email verification tokens"""
    
    def __init__(self, user_id, token, expires_at, created_at=None, id=None):
        if id is None:
            self.id = _email_verification_id_counter[0]
            _email_verification_id_counter[0] += 1
        else:
            self.id = id
            if id >= _email_verification_id_counter[0]:
                _email_verification_id_counter[0] = id + 1
        
        self.user_id = user_id
        self.token = token
        self.expires_at = expires_at
        self.created_at = created_at or datetime.utcnow()
        
        # Store in memory
        email_verifications_storage[token] = self
    
    @staticmethod
    def generate_token():
        """Generate a secure verification token"""
        return secrets.token_urlsafe(32)
    
    def is_expired(self):
        """Check if token is expired"""
        return datetime.utcnow() > self.expires_at
    
    @staticmethod
    def query_by_token(token):
        """Query verification by token"""
        return email_verifications_storage.get(token)
    
    @staticmethod
    def delete_by_token(token):
        """Delete verification token"""
        if token in email_verifications_storage:
            del email_verifications_storage[token]
            return True
        return False
    
    def __repr__(self):
        return f'<EmailVerification for user {self.user_id}>'
