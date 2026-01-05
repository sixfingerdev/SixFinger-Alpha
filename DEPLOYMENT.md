# Deployment Guide for SixFinger Alpha

This guide covers deploying the SixFinger Alpha Flask application to production.

## Prerequisites

- Python 3.8+
- PostgreSQL or MySQL (recommended for production)
- Redis (for rate limiting)
- Stripe account
- Email service (Gmail, SendGrid, etc.)
- Domain name and SSL certificate

## Environment Setup

1. **Clone the repository**:
```bash
git clone https://github.com/sixfingerdev/SixFinger-Alpha.git
cd SixFinger-Alpha
```

2. **Create virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

## Configuration

1. **Set up environment variables** (`.env`):
```env
# Production mode
FLASK_ENV=production
SECRET_KEY=your-strong-random-secret-key-here

# Database (PostgreSQL recommended)
DATABASE_URL=postgresql://user:password@localhost/sixfinger

# Stripe
STRIPE_PUBLIC_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Email
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USERNAME=apikey
MAIL_PASSWORD=your-sendgrid-api-key
MAIL_DEFAULT_SENDER=noreply@yourdomain.com

# Redis (for rate limiting)
REDIS_URL=redis://localhost:6379/0

# Server
PORT=5000
```

2. **Generate a secure secret key**:
```python
python -c "import secrets; print(secrets.token_hex(32))"
```

## Database Setup

### PostgreSQL

1. **Install PostgreSQL**:
```bash
sudo apt-get install postgresql postgresql-contrib
```

2. **Create database and user**:
```bash
sudo -u postgres psql
CREATE DATABASE sixfinger;
CREATE USER sixfinger_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE sixfinger TO sixfinger_user;
\q
```

3. **Update DATABASE_URL** in `.env`:
```
DATABASE_URL=postgresql://sixfinger_user:your_password@localhost/sixfinger
```

### Initialize Database

```bash
python run.py
# Database tables will be created automatically
```

## Redis Setup

1. **Install Redis**:
```bash
sudo apt-get install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

2. **Test Redis**:
```bash
redis-cli ping
# Should return: PONG
```

## Stripe Configuration

1. **Get your Stripe keys** from [Stripe Dashboard](https://dashboard.stripe.com/apikeys)
2. **Set up webhook endpoint**:
   - URL: `https://yourdomain.com/subscription/webhook`
   - Events to listen for:
     - `checkout.session.completed`
     - `customer.subscription.updated`
     - `customer.subscription.deleted`
3. **Copy webhook secret** to `.env`

## Email Configuration

### Using Gmail

1. **Enable 2FA** on your Gmail account
2. **Generate App Password**: Google Account → Security → App passwords
3. **Configure in `.env`**:
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### Using SendGrid

1. **Sign up** at [SendGrid](https://sendgrid.com/)
2. **Create API key**
3. **Configure in `.env`**:
```env
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USERNAME=apikey
MAIL_PASSWORD=your-sendgrid-api-key
```

## Running with Gunicorn

1. **Test locally**:
```bash
gunicorn -w 4 -b 127.0.0.1:5000 run:app
```

2. **Create systemd service** (`/etc/systemd/system/sixfinger.service`):
```ini
[Unit]
Description=SixFinger Alpha Flask Application
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/SixFinger-Alpha
Environment="PATH=/var/www/SixFinger-Alpha/venv/bin"
ExecStart=/var/www/SixFinger-Alpha/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 run:app
Restart=always

[Install]
WantedBy=multi-user.target
```

3. **Start service**:
```bash
sudo systemctl start sixfinger
sudo systemctl enable sixfinger
sudo systemctl status sixfinger
```

## Nginx Configuration

1. **Install Nginx**:
```bash
sudo apt-get install nginx
```

2. **Create site configuration** (`/etc/nginx/sites-available/sixfinger`):
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /var/www/SixFinger-Alpha/app/static;
        expires 30d;
    }
}
```

3. **Enable site**:
```bash
sudo ln -s /etc/nginx/sites-available/sixfinger /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## SSL Certificate (Let's Encrypt)

1. **Install Certbot**:
```bash
sudo apt-get install certbot python3-certbot-nginx
```

2. **Obtain certificate**:
```bash
sudo certbot --nginx -d yourdomain.com
```

3. **Auto-renewal**:
```bash
sudo certbot renew --dry-run
```

## Create Admin User

```bash
python create_admin.py
```

## Monitoring and Logs

### View application logs:
```bash
sudo journalctl -u sixfinger -f
```

### View Nginx logs:
```bash
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## Security Checklist

- [ ] Set strong `SECRET_KEY`
- [ ] Use PostgreSQL/MySQL instead of SQLite
- [ ] Enable HTTPS with valid SSL certificate
- [ ] Configure firewall (UFW)
- [ ] Set up Redis authentication
- [ ] Configure rate limiting
- [ ] Enable database backups
- [ ] Monitor application logs
- [ ] Set up error tracking (Sentry)
- [ ] Configure CORS properly
- [ ] Use environment variables for secrets
- [ ] Keep dependencies updated

## Backup Strategy

### Database backup:
```bash
# PostgreSQL
pg_dump -U sixfinger_user sixfinger > backup.sql

# Restore
psql -U sixfinger_user sixfinger < backup.sql
```

### Full backup script:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -U sixfinger_user sixfinger > /backups/db_$DATE.sql
tar -czf /backups/app_$DATE.tar.gz /var/www/SixFinger-Alpha
# Upload to S3 or remote storage
```

## Troubleshooting

### Application won't start:
```bash
# Check logs
sudo journalctl -u sixfinger -n 50

# Test configuration
python -c "from app import create_app; app = create_app(); print('OK')"
```

### Database connection error:
```bash
# Test PostgreSQL connection
psql -U sixfinger_user -d sixfinger -h localhost
```

### Stripe webhook not working:
1. Check webhook endpoint is accessible
2. Verify webhook secret in `.env`
3. Check Nginx proxy configuration
4. View Stripe Dashboard webhook logs

## Performance Optimization

1. **Use CDN** for static files
2. **Enable gzip** compression in Nginx
3. **Configure caching** headers
4. **Use connection pooling** for database
5. **Optimize database queries** with indexes
6. **Monitor with APM** tools (New Relic, Datadog)

## Docker Deployment (Optional)

See `docker-compose.yml` for containerized deployment.

```bash
docker-compose up -d
```

## Support

For deployment issues, contact support@sixfinger.dev
