from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, Subscription, EmailVerification
from datetime import datetime, timedelta
import re

auth_bp = Blueprint('auth', __name__)

def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_valid_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    return True, ""

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        
        if not email or not password:
            flash('Please provide both email and password', 'error')
            return render_template('auth/login.html')
        
        user = User.query_by_email(email)
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact support.', 'error')
                return render_template('auth/login.html')
            
            login_user(user, remember=remember)
            user.last_login = datetime.utcnow()
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        
        # Validation
        if not username or not email or not password:
            flash('All fields are required', 'error')
            return render_template('auth/signup.html')
        
        if len(username) < 3:
            flash('Username must be at least 3 characters long', 'error')
            return render_template('auth/signup.html')
        
        if not is_valid_email(email):
            flash('Please provide a valid email address', 'error')
            return render_template('auth/signup.html')
        
        if password != password_confirm:
            flash('Passwords do not match', 'error')
            return render_template('auth/signup.html')
        
        is_valid, error_msg = is_valid_password(password)
        if not is_valid:
            flash(error_msg, 'error')
            return render_template('auth/signup.html')
        
        # Check if user exists
        if User.query_by_email(email):
            flash('Email already registered', 'error')
            return render_template('auth/signup.html')
        
        if User.query_by_username(username):
            flash('Username already taken', 'error')
            return render_template('auth/signup.html')
        
        # Create user
        try:
            user = User(username=username, email=email)
            user.set_password(password)
            
            # Create free subscription
            subscription = Subscription(user_id=user.id, plan='free')
            
            # Create email verification token
            token = EmailVerification.generate_token()
            verification = EmailVerification(
                user_id=user.id,
                token=token,
                expires_at=datetime.utcnow() + timedelta(days=1)
            )
            
            # TODO: Send verification email
            
            flash('Account created successfully! Please check your email to verify your account.', 'success')
            return redirect(url_for('auth.login'))
        except ValueError as e:
            flash(str(e), 'error')
            return render_template('auth/signup.html')
    
    return render_template('auth/signup.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/verify-email/<token>')
def verify_email(token):
    """Verify email address"""
    verification = EmailVerification.query_by_token(token)
    
    if not verification:
        flash('Invalid verification token', 'error')
        return redirect(url_for('main.index'))
    
    if verification.is_expired():
        flash('Verification token has expired', 'error')
        return redirect(url_for('main.index'))
    
    user = User.query_by_id(verification.user_id)
    if user:
        user.email_verified = True
        EmailVerification.delete_by_token(token)
        flash('Email verified successfully! You can now log in.', 'success')
    
    return redirect(url_for('auth.login'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Request password reset"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        
        user = User.query_by_email(email)
        if user:
            # TODO: Send password reset email
            pass
        
        flash('If an account exists with that email, you will receive password reset instructions.', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html')
