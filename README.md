# NEXUS // Cyberpunk B2B Networking Platform

A stylized, cyberpunk-themed business networking forum and messaging platform built with Python (Flask).

## Features
- User registration & login (secure password hashing)
- Editable business profiles (company + bio + **avatar upload**)
- Discussion forum with **search**, categories, and **file attachments**
- Direct messaging between users
- **Notifications** system (new messages & replies)
- User directory
- **Real Stripe payments** for Premium access
- **Admin panel** (manage users, premium status, delete posts)
- Global unread counters in navigation
- Full cyberpunk / hacker aesthetic

## Setup & Run

1. Navigate to the project folder:
   ```bash
   cd cyberpunk_b2b
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. **Stripe setup** (required for real payments):
   - Create a Stripe account and get test keys from the dashboard.
   - Create a Product + Price (one-time or recurring).
   - Set up a webhook endpoint pointing to: `https://your-domain.com/webhook/stripe`
     - Listen for `checkout.session.completed`
     - Copy the webhook signing secret (`whsec_...`)
   - Set environment variables before running:
     ```bash
     export STRIPE_SECRET_KEY=sk_test_...
     export STRIPE_PUBLISHABLE_KEY=pk_test_...
     export STRIPE_PRICE_ID=price_...
     export STRIPE_WEBHOOK_SECRET=whsec_...
     export SECRET_KEY=your-random-secret
     ```
   - Or create a `.env` file and load it (python-dotenv is included).

   **Local testing**: Use the Stripe CLI:
   ```bash
   stripe listen --forward-to localhost:5000/webhook/stripe
   ```

5. Run the application:
   ```bash
   python app.py
   ```

6. Open your browser to: **http://127.0.0.1:5000**

## Making yourself Admin
After registering, open a Python shell:
```bash
python
>>> from app import create_app, db
>>> from models import User
>>> app = create_app()
>>> with app.app_context():
...     user = User.query.filter_by(username='your_username').first()
...     user.is_admin = True
...     db.session.commit()
```

## Production Notes
- Use a proper database (PostgreSQL) instead of SQLite.
- Serve uploads securely or use cloud storage (S3, etc.).
- Add HTTPS, rate limiting, and CSRF protection for production.
- Stripe webhooks with signature verification are implemented for secure, reliable payment confirmation.

## Aesthetic
Inspired by classic cyberpunk visuals (neon on black, terminal fonts, scan lines, glitch text) — purely cosmetic.

Built for legitimate B2B networking and discussion.
