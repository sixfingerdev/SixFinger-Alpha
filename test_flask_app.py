#!/usr/bin/env python3
"""
Test script for SixFinger Alpha Flask application
"""
from app import create_app, db
from app.models import User, Subscription, APIKey, APIUsage
from datetime import datetime

def test_app():
    """Test application initialization"""
    print("Testing Flask application...")
    
    app = create_app()
    
    with app.app_context():
        # Test database creation
        print("\n1. Testing database setup...")
        db.create_all()
        print("   Database tables created successfully")
        
        # Test user creation
        print("\n2. Testing user model...")
        test_user = User(
            username='testuser',
            email='test@example.com',
            is_active=True
        )
        test_user.set_password('TestPassword123')
        db.session.add(test_user)
        db.session.flush()
        
        # Test password checking
        assert test_user.check_password('TestPassword123'), "Password check failed"
        assert not test_user.check_password('wrongpassword'), "Password check should fail"
        print("   User model working correctly")
        
        # Test subscription
        print("\n3. Testing subscription model...")
        subscription = Subscription(
            user_id=test_user.id,
            plan='free'
        )
        db.session.add(subscription)
        db.session.flush()
        
        assert test_user.get_plan() == 'free', "Subscription plan check failed"
        print("   Subscription model working correctly")
        
        # Test API key generation
        print("\n4. Testing API key model...")
        api_key = APIKey(
            user_id=test_user.id,
            key=APIKey.generate_key(),
            name='Test API Key'
        )
        db.session.add(api_key)
        
        assert api_key.key.startswith('sk_'), "API key format incorrect"
        assert len(api_key.key) == 51, "API key length incorrect"  # sk_ + 48 chars
        print("   API key model working correctly")
        
        # Test API usage tracking
        print("\n5. Testing API usage model...")
        usage = APIUsage(
            user_id=test_user.id,
            api_key_id=api_key.id,
            endpoint='/api/v1/query',
            method='POST',
            status_code=200,
            response_time=0.5
        )
        db.session.add(usage)
        
        # Test rate limiting
        assert test_user.can_make_request(), "Rate limit check failed"
        print("   API usage tracking working correctly")
        
        # Rollback to not save test data
        db.session.rollback()
        print("\n6. Rolling back test data...")
        
        print("\n" + "="*50)
        print("All tests passed successfully!")
        print("="*50)
        
        # Print registered blueprints
        print("\nRegistered blueprints:")
        for blueprint in app.blueprints:
            print(f"  - {blueprint}")
        
        # Print registered routes (sample)
        print("\nSample routes:")
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(str(rule))
        
        for route in sorted(routes)[:20]:
            print(f"  {route}")
        
        print(f"\nTotal routes: {len(routes)}")

if __name__ == "__main__":
    test_app()
