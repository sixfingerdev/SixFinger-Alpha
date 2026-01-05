from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app.models import db, Subscription
import stripe
from datetime import datetime

subscription_bp = Blueprint('subscription', __name__)

def init_stripe():
    """Initialize Stripe with secret key"""
    stripe.api_key = current_app.config.get('STRIPE_SECRET_KEY')

@subscription_bp.route('/plans')
@login_required
def plans():
    """View available subscription plans"""
    plans = current_app.config['SUBSCRIPTION_PLANS']
    current_plan = current_user.get_plan()
    currency = request.args.get('currency', 'USD')
    
    return render_template('subscription/plans.html',
                         plans=plans,
                         current_plan=current_plan,
                         currency=currency)

@subscription_bp.route('/manage')
@login_required
def manage():
    """Manage current subscription"""
    subscription = current_user.subscription
    plans = current_app.config['SUBSCRIPTION_PLANS']
    
    return render_template('subscription/manage.html',
                         subscription=subscription,
                         plans=plans)

@subscription_bp.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    """Create Stripe checkout session"""
    init_stripe()
    
    plan = request.form.get('plan')
    currency = request.form.get('currency', 'USD').upper()
    
    if plan not in current_app.config['SUBSCRIPTION_PLANS']:
        flash('Invalid plan selected', 'error')
        return redirect(url_for('subscription.plans'))
    
    if currency not in current_app.config['SUPPORTED_CURRENCIES']:
        flash('Invalid currency selected', 'error')
        return redirect(url_for('subscription.plans'))
    
    plan_config = current_app.config['SUBSCRIPTION_PLANS'][plan]
    price_key = f'price_{currency.lower()}'
    price = plan_config.get(price_key, 0)
    
    if price == 0:
        flash('Cannot create checkout for free plan', 'error')
        return redirect(url_for('subscription.plans'))
    
    try:
        # Create or get Stripe customer
        if current_user.subscription and current_user.subscription.stripe_customer_id:
            customer_id = current_user.subscription.stripe_customer_id
        else:
            customer = stripe.Customer.create(
                email=current_user.email,
                metadata={'user_id': current_user.id}
            )
            customer_id = customer.id
            
            if not current_user.subscription:
                subscription = Subscription(user_id=current_user.id)
                db.session.add(subscription)
            
            current_user.subscription.stripe_customer_id = customer_id
            db.session.commit()
        
        # Create checkout session
        checkout_session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': currency.lower(),
                    'product_data': {
                        'name': f'SixFinger {plan_config["name"]} Plan',
                        'description': ', '.join(plan_config['features'][:3]),
                    },
                    'unit_amount': int(price * 100),  # Stripe uses cents
                    'recurring': {
                        'interval': 'month',
                    },
                },
                'quantity': 1,
            }],
            mode='subscription',
            success_url=url_for('subscription.success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('subscription.plans', _external=True),
            metadata={
                'user_id': current_user.id,
                'plan': plan
            }
        )
        
        return redirect(checkout_session.url, code=303)
    
    except stripe.error.StripeError as e:
        flash(f'Payment error: {str(e)}', 'error')
        return redirect(url_for('subscription.plans'))

@subscription_bp.route('/success')
@login_required
def success():
    """Handle successful subscription"""
    session_id = request.args.get('session_id')
    
    if not session_id:
        flash('Invalid session', 'error')
        return redirect(url_for('main.dashboard'))
    
    init_stripe()
    
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        
        if session.payment_status == 'paid':
            flash('Subscription activated successfully!', 'success')
        else:
            flash('Payment is being processed', 'info')
    
    except stripe.error.StripeError as e:
        flash('Error verifying payment', 'error')
    
    return redirect(url_for('main.dashboard'))

@subscription_bp.route('/cancel', methods=['POST'])
@login_required
def cancel():
    """Cancel subscription"""
    subscription = current_user.subscription
    
    if not subscription or not subscription.stripe_subscription_id:
        flash('No active subscription found', 'error')
        return redirect(url_for('subscription.manage'))
    
    init_stripe()
    
    try:
        stripe.Subscription.modify(
            subscription.stripe_subscription_id,
            cancel_at_period_end=True
        )
        
        subscription.cancel_at_period_end = True
        db.session.commit()
        
        flash('Subscription will be cancelled at the end of the billing period', 'info')
    
    except stripe.error.StripeError as e:
        flash(f'Error cancelling subscription: {str(e)}', 'error')
    
    return redirect(url_for('subscription.manage'))

@subscription_bp.route('/webhook', methods=['POST'])
def webhook():
    """Handle Stripe webhooks"""
    init_stripe()
    
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = current_app.config.get('STRIPE_WEBHOOK_SECRET')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Handle different event types
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_checkout_complete(session)
    
    elif event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        handle_subscription_updated(subscription)
    
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        handle_subscription_deleted(subscription)
    
    return jsonify({'status': 'success'}), 200

def handle_checkout_complete(session):
    """Handle completed checkout"""
    user_id = session['metadata'].get('user_id')
    plan = session['metadata'].get('plan')
    
    if user_id and plan:
        subscription = Subscription.query.filter_by(user_id=user_id).first()
        if subscription:
            subscription.plan = plan
            subscription.is_active = True
            subscription.stripe_subscription_id = session.get('subscription')
            db.session.commit()

def handle_subscription_updated(stripe_subscription):
    """Handle subscription update"""
    subscription = Subscription.query.filter_by(
        stripe_subscription_id=stripe_subscription['id']
    ).first()
    
    if subscription:
        subscription.current_period_start = datetime.fromtimestamp(
            stripe_subscription['current_period_start']
        )
        subscription.current_period_end = datetime.fromtimestamp(
            stripe_subscription['current_period_end']
        )
        subscription.cancel_at_period_end = stripe_subscription.get('cancel_at_period_end', False)
        db.session.commit()

def handle_subscription_deleted(stripe_subscription):
    """Handle subscription deletion"""
    subscription = Subscription.query.filter_by(
        stripe_subscription_id=stripe_subscription['id']
    ).first()
    
    if subscription:
        subscription.plan = 'free'
        subscription.is_active = False
        subscription.stripe_subscription_id = None
        db.session.commit()
