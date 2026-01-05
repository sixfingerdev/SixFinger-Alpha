import os
from datetime import timedelta

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Flask-Login
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
    
    # Stripe configuration
    STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    # Currency settings
    SUPPORTED_CURRENCIES = ['USD', 'TRY']
    USD_TO_TRY_RATE = 47.0
    DEFAULT_CURRENCY = 'USD'
    
    # Email configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@sixfinger.dev')
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'memory://')
    RATELIMIT_DEFAULT = "200 per day, 50 per hour"
    
    # API Configuration
    API_RATE_LIMITS = {
        'free': {'daily': 100, 'monthly': 1000},
        'starter': {'daily': 1000, 'monthly': 25000},
        'pro': {'daily': 10000, 'monthly': 250000},
        'enterprise': {'daily': -1, 'monthly': -1}  # Unlimited
    }
    
    # Subscription Plans
    SUBSCRIPTION_PLANS = {
        'free': {
            'name': 'Free',
            'price_usd': 0,
            'price_try': 0,
            'features': [
                'Basic API access',
                '100 requests per day',
                '1,000 requests per month',
                'Community support'
            ]
        },
        'starter': {
            'name': 'Starter',
            'price_usd': 9,
            'price_try': 423,  # 9 * 47
            'features': [
                'Enhanced API access',
                '1,000 requests per day',
                '25,000 requests per month',
                'Email support',
                'API documentation'
            ]
        },
        'pro': {
            'name': 'Pro',
            'price_usd': 49,
            'price_try': 2303,  # 49 * 47
            'features': [
                'Full API access',
                '10,000 requests per day',
                '250,000 requests per month',
                'Priority support',
                'Advanced features',
                'Custom integrations'
            ]
        },
        'enterprise': {
            'name': 'Enterprise',
            'price_usd': 299,
            'price_try': 14053,  # 299 * 47
            'features': [
                'Unlimited API access',
                'Dedicated support',
                'Custom solutions',
                'SLA guarantee',
                'White-label options',
                'Dedicated account manager'
            ]
        }
    }

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
