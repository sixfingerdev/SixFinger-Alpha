# SixFinger Alpha - Flask Web Application

A full-featured Flask web application with authentication, subscription management, API access, and admin panel.

## Features

- **User Authentication**: Secure login/signup with password hashing
- **Subscription Plans**: Multiple tiers (Free, Starter, Pro, Enterprise)
- **Stripe Integration**: Payment processing with support for USD and TRY currencies
- **Developer Portal**: API key management and usage tracking
- **Admin Panel**: User management, analytics, and system monitoring
- **API Endpoints**: RESTful API for AI services
- **Security**: CSRF protection, rate limiting, secure headers
- **Email Verification**: User email verification system
- **Responsive Design**: Mobile-friendly interface

## Installation

1. Clone the repository:
```bash
git clone https://github.com/sixfingerdev/SixFinger-Alpha.git
cd SixFinger-Alpha
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize the database:
```bash
python run.py
# Database will be created automatically on first run
```

## Configuration

Edit `.env` file with your settings:

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///sixfinger.db

# Stripe keys (get from https://stripe.com)
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Email configuration
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

## Running the Application

### Development Mode
```bash
python run.py
```

The application will be available at `http://localhost:5000`

### Production Mode
```bash
export FLASK_ENV=production
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

## Project Structure

```
SixFinger-Alpha/
├── app/
│   ├── __init__.py           # Application factory
│   ├── models.py             # Database models
│   ├── blueprints/           # Application blueprints
│   │   ├── auth.py           # Authentication routes
│   │   ├── main.py           # Main routes
│   │   ├── api.py            # API endpoints
│   │   ├── admin.py          # Admin panel
│   │   ├── developer.py      # Developer portal
│   │   └── subscription.py   # Subscription management
│   ├── templates/            # HTML templates
│   └── static/               # CSS, JS, images
├── config.py                 # Configuration
├── run.py                    # Application entry point
├── requirements.txt          # Python dependencies
└── .env.example             # Example environment variables
```

## Subscription Plans

| Plan       | Price (USD) | Price (TRY) | Daily Requests | Monthly Requests |
|------------|-------------|-------------|----------------|------------------|
| Free       | $0          | 0₺          | 100            | 1,000            |
| Starter    | $9          | 423₺        | 1,000          | 25,000           |
| Pro        | $49         | 2,303₺      | 10,000         | 250,000          |
| Enterprise | $299        | 14,053₺     | Unlimited      | Unlimited        |

Exchange rate: 1 USD = 47 TRY

## API Usage

### Authentication
All API requests require an API key:
```bash
curl -H "X-API-Key: your_api_key_here" https://yourdomain.com/api/v1/query
```

### Example Request
```bash
curl -X POST https://yourdomain.com/api/v1/query \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explain quantum computing"}'
```

## Admin Access

To create an admin user, use the Python shell:
```bash
python
>>> from app import create_app, db
>>> from app.models import User
>>> app = create_app()
>>> with app.app_context():
...     user = User.query.filter_by(email='your@email.com').first()
...     user.is_admin = True
...     db.session.commit()
```

## Security Features

- Password hashing with bcrypt
- CSRF protection on all forms
- Rate limiting on API endpoints
- Secure session cookies
- SQL injection protection via SQLAlchemy
- XSS protection headers
- Input validation and sanitization

## Development

### Running Tests
```bash
pytest
```

### Code Style
Follow PEP 8 guidelines for Python code.

## License

MIT License

## Support

For support, email support@sixfinger.dev or visit our contact page.

## Built With

- Flask - Web framework
- SQLAlchemy - ORM
- Stripe - Payment processing
- Flask-Login - User session management
- Flask-Bcrypt - Password hashing
- Bootstrap/Custom CSS - Frontend styling

---

Built with care by SixFinger Dev
