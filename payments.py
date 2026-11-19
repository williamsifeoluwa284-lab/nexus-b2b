import os
import stripe
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import db

payments = Blueprint('payments', __name__)

# Load Stripe keys from environment
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_your_secret_key_here')
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY', 'pk_test_your_publishable_key_here')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', 'whsec_your_webhook_secret_here')
PREMIUM_PRICE_ID = os.environ.get('STRIPE_PRICE_ID', 'price_your_price_id_here')

@payments.route('/premium')
@login_required
def premium():
    return render_template('premium.html', publishable_key=STRIPE_PUBLISHABLE_KEY)

@payments.route('/premium/checkout', methods=['POST'])
@login_required
def checkout():
    if current_user.is_premium:
        flash('You already have premium access.', 'info')
        return redirect(url_for('main.dashboard'))

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': PREMIUM_PRICE_ID,
                'quantity': 1,
            }],
            mode='payment',
            success_url=url_for('payments.success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('payments.premium', _external=True),
            customer_email=current_user.email,
            metadata={'user_id': str(current_user.id)}
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        flash(f'Payment error: {str(e)}', 'danger')
        return redirect(url_for('payments.premium'))

@payments.route('/premium/success')
@login_required
def success():
    # Client-side success page — actual activation happens via webhook
    flash('Payment received. Premium access will activate shortly.', 'success')
    return redirect(url_for('main.dashboard'))

@payments.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    """Secure Stripe webhook endpoint with signature verification."""
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')

    if not sig_header:
        return jsonify({'error': 'Missing signature'}), 400

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        # Invalid payload
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return jsonify({'error': 'Invalid signature'}), 400

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session.get('metadata', {}).get('user_id')

        if user_id and session.get('payment_status') == 'paid':
            from models import User, Notification
            user = User.query.get(int(user_id))
            if user and not user.is_premium:
                user.is_premium = True
                # Create notification
                notif = Notification(
                    message='Premium access activated! Welcome to the Inner Circle.',
                    link=url_for('main.dashboard'),
                    user_id=user.id
                )
                db.session.add(notif)
                db.session.commit()

    elif event['type'] == 'checkout.session.expired':
        # Optional: log or notify about expired sessions
        pass

    return jsonify({'status': 'success'}), 200
