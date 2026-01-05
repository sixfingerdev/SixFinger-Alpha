#!/usr/bin/env python3
"""
Script to create an admin user for SixFinger Alpha
"""
import sys
from app import create_app
from app.models import User, Subscription

def create_admin():
    """Create an admin user"""
    app = create_app()
    
    with app.app_context():
        print("Creating admin user...")
        
        # Check if admin exists
        admin_email = input("Enter admin email: ").strip().lower()
        existing = User.query_by_email(admin_email)
        
        if existing:
            print(f"User with email {admin_email} already exists.")
            make_admin = input("Make this user an admin? (y/n): ").strip().lower()
            if make_admin == 'y':
                existing.is_admin = True
                existing.email_verified = True
                print(f"User {existing.username} is now an admin!")
            return
        
        # Create new admin user
        username = input("Enter admin username: ").strip()
        password = input("Enter admin password: ").strip()
        
        if len(password) < 8:
            print("Password must be at least 8 characters long")
            sys.exit(1)
        
        user = User(
            email=admin_email,
            username=username,
            is_admin=True,
            is_active=True,
            email_verified=True
        )
        user.set_password(password)
        
        # Create subscription
        subscription = Subscription(
            user_id=user.id,
            plan='enterprise'
        )
        
        print(f"\nAdmin user created successfully!")
        print(f"Username: {username}")
        print(f"Email: {admin_email}")
        print(f"You can now log in at /login")

if __name__ == "__main__":
    create_admin()
