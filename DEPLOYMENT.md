# 🚀 Deployment Guide

Complete guide for deploying your SlayFashion backend to production.

## Table of Contents

1. [Railway (Recommended)](#railway-deployment)
2. [Heroku](#heroku-deployment)
3. [DigitalOcean](#digitalocean-deployment)
4. [AWS EC2](#aws-ec2-deployment)
5. [Docker](#docker-deployment)

---

## Railway Deployment (Recommended) ⚡

Railway is the easiest and most affordable option for FastAPI apps.

### Prerequisites
- GitHub account
- Railway account (https://railway.app)

### Step 1: Prepare Your Code

```bash
# Make sure everything is committed
git add .
git commit -m "Ready for deployment"
git push origin main
```

### Step 2: Deploy to Railway

1. Go to https://railway.app
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository
5. Railway will auto-detect the Python app

### Step 3: Add PostgreSQL

1. In your project, click **"New"** → **"Database"** → **"PostgreSQL"**
2. Railway will automatically set `DATABASE_URL` environment variable

### Step 4: Set Environment Variables

In your Railway project settings, add:

```
SHOPIFY_STORE_DOMAIN=f3lifestyle.myshopify.com
SHOPIFY_ADMIN_API_TOKEN=shpat_xxxxxxxxxxxxx
SHOPIFY_STOREFRONT_ACCESS_TOKEN=your_storefront_token
SHOPIFY_API_VERSION=2024-10

TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890

JWT_SECRET_KEY=your-super-secret-production-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=10080

OTP_EXPIRATION_MINUTES=10
OTP_LENGTH=6

HOST=0.0.0.0
PORT=8000
```

### Step 5: Deploy

Railway will automatically deploy! You'll get a URL like:
```
https://your-app.railway.app
```

### Step 6: Test

```bash
curl https://your-app.railway.app/health
```

**Cost**: $5-20/month (very affordable!)

---

## Heroku Deployment

### Step 1: Install Heroku CLI

```bash
# macOS
brew tap heroku/brew && brew install heroku

# Or download from https://devcenter.heroku.com/articles/heroku-cli
```

### Step 2: Login and Create App

```bash
heroku login
heroku create slayfashion-backend
```

### Step 3: Add PostgreSQL

```bash
heroku addons:create heroku-postgresql:mini
```

### Step 4: Set Environment Variables

```bash
heroku config:set SHOPIFY_STORE_DOMAIN=f3lifestyle.myshopify.com
heroku config:set SHOPIFY_ADMIN_API_TOKEN=shpat_xxxxxxxxxxxxx
heroku config:set SHOPIFY_STOREFRONT_ACCESS_TOKEN=your_token
heroku config:set SHOPIFY_API_VERSION=2024-10

heroku config:set TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxx
heroku config:set TWILIO_AUTH_TOKEN=your_auth_token
heroku config:set TWILIO_PHONE_NUMBER=+1234567890

heroku config:set JWT_SECRET_KEY=your-super-secret-key
```

### Step 5: Create Procfile

```bash
echo "web: python run.py" > Procfile
```

### Step 6: Deploy

```bash
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

### Step 7: Scale

```bash
heroku ps:scale web=1
```

Your app will be at: `https://slayfashion-backend.herokuapp.com`

**Cost**: $7-50/month

---

## DigitalOcean Deployment

### Option A: App Platform (Easiest)

1. Go to https://cloud.digitalocean.com/apps
2. Click **"Create App"**
3. Connect your GitHub repo
4. Choose:
   - **Type**: Web Service
   - **Build Command**: `pip install -r requirements.txt`
   - **Run Command**: `python run.py`
5. Add PostgreSQL database (managed)
6. Set environment variables
7. Deploy!

**Cost**: $12-50/month

### Option B: Droplet (More Control)

#### Step 1: Create Droplet

```bash
# From DigitalOcean console, create Ubuntu 22.04 droplet
# Choose: Basic plan, $6/month, 1GB RAM
```

#### Step 2: SSH and Setup

```bash
ssh root@your-droplet-ip

# Update system
apt update && apt upgrade -y

# Install Python and PostgreSQL
apt install python3.11 python3-pip python3-venv postgresql postgresql-contrib nginx -y

# Create app user
adduser slayfashion
usermod -aG sudo slayfashion
su - slayfashion
```

#### Step 3: Deploy App

```bash
# Clone your repo
git clone https://github.com/yourusername/slayfashionbackend.git
cd slayfashionbackend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
nano .env
# (paste your environment variables)
```

#### Step 4: Setup PostgreSQL

```bash
sudo -u postgres psql

CREATE DATABASE slayfashion;
CREATE USER slayfashion WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE slayfashion TO slayfashion;
\q
```

Update `.env`:
```
DATABASE_URL=postgresql://slayfashion:your_secure_password@localhost:5432/slayfashion
```

#### Step 5: Setup Systemd Service

```bash
sudo nano /etc/systemd/system/slayfashion.service
```

Paste:
```ini
[Unit]
Description=SlayFashion Backend API
After=network.target

[Service]
User=slayfashion
WorkingDirectory=/home/slayfashion/slayfashionbackend
Environment="PATH=/home/slayfashion/slayfashionbackend/venv/bin"
EnvironmentFile=/home/slayfashion/slayfashionbackend/.env
ExecStart=/home/slayfashion/slayfashionbackend/venv/bin/python run.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
sudo systemctl start slayfashion
sudo systemctl enable slayfashion
sudo systemctl status slayfashion
```

#### Step 6: Setup Nginx

```bash
sudo nano /etc/nginx/sites-available/slayfashion
```

Paste:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable:
```bash
sudo ln -s /etc/nginx/sites-available/slayfashion /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### Step 7: Setup SSL (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

**Cost**: $6-20/month

---

## AWS EC2 Deployment

### Step 1: Create EC2 Instance

1. Go to AWS Console → EC2
2. Launch Instance:
   - **AMI**: Ubuntu Server 22.04 LTS
   - **Instance Type**: t2.micro (free tier) or t2.small
   - **Security Group**: Allow ports 22 (SSH), 80 (HTTP), 443 (HTTPS)

### Step 2: Connect and Setup

```bash
ssh -i your-key.pem ubuntu@your-ec2-ip

# Follow same steps as DigitalOcean Droplet Option B
```

### Step 3: Use RDS for Database (Optional)

1. Create RDS PostgreSQL instance
2. Update `DATABASE_URL` in `.env`

**Cost**: Free tier eligible, then $10-100/month

---

## Docker Deployment

### Local Docker Test

```bash
# Build image
docker build -t slayfashion-backend .

# Run with docker-compose
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop
docker-compose down
```

### Deploy to Any Docker Host

Your app is now containerized and can be deployed to:
- AWS ECS/Fargate
- Google Cloud Run
- Azure Container Instances
- Any VPS with Docker

---

## Post-Deployment Checklist

### ✅ Security

- [ ] HTTPS enabled (SSL certificate)
- [ ] Environment variables set (not hardcoded)
- [ ] Firewall configured
- [ ] Database password is strong
- [ ] JWT secret key is random and secure
- [ ] Shopify API tokens are valid

### ✅ Database

- [ ] PostgreSQL is running
- [ ] Database migrations applied
- [ ] Backups configured (daily recommended)

### ✅ Monitoring

- [ ] Health endpoint accessible (`/health`)
- [ ] Logs are being collected
- [ ] Error tracking setup (Sentry recommended)
- [ ] Uptime monitoring (UptimeRobot, Pingdom)

### ✅ Performance

- [ ] Rate limiting enabled
- [ ] Database connection pooling
- [ ] Caching configured (Redis for production)

### ✅ Testing

- [ ] API endpoints work
- [ ] OTP sending works
- [ ] OTP verification works
- [ ] Shopify integration works
- [ ] Mobile app can connect

---

## Update Frontend with Production URL

After deployment, update your React Native app:

```typescript
// src/config/backend.ts
export const BACKEND_CONFIG = {
  apiUrl: __DEV__ 
    ? 'http://10.0.2.2:8000'  // Development
    : 'https://your-production-api.railway.app',  // Production
};
```

---

## Monitoring & Maintenance

### Recommended Tools

1. **Error Tracking**: Sentry (https://sentry.io)
   ```bash
   pip install sentry-sdk
   ```

2. **Uptime Monitoring**: UptimeRobot (https://uptimerobot.com)
   - Monitor: `https://your-api.com/health`
   - Get alerts when down

3. **Logs**: Papertrail or Logtail
   - View all logs in one place
   - Search and filter

4. **Performance**: New Relic or DataDog
   - Track response times
   - Database query performance

### Database Backups

#### Railway / Heroku
Automatic backups are included!

#### Self-Hosted (DigitalOcean/AWS)

```bash
# Create backup script
nano ~/backup_db.sh
```

```bash
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
pg_dump -U slayfashion slayfashion > /backups/slayfashion_$TIMESTAMP.sql
# Keep only last 7 days
find /backups -name "slayfashion_*.sql" -mtime +7 -delete
```

```bash
chmod +x ~/backup_db.sh

# Add to crontab (daily at 2 AM)
crontab -e
0 2 * * * /home/slayfashion/backup_db.sh
```

---

## Scaling

### When to Scale?

- Response times > 1 second
- CPU usage consistently > 70%
- Error rate increasing
- Traffic spike expected

### Horizontal Scaling

1. **Add More Instances**
   - Railway: Increase replicas
   - Heroku: `heroku ps:scale web=2`
   - Docker: Scale with docker-compose

2. **Add Load Balancer**
   - DigitalOcean Load Balancer
   - AWS ELB
   - Nginx (self-hosted)

3. **Use Redis for Rate Limiting**
   Replace in-memory rate limiter with Redis:
   ```bash
   pip install redis
   ```

### Vertical Scaling

Upgrade instance size:
- Railway: Increase plan
- Heroku: Upgrade dyno type
- VPS: Resize droplet

---

## Troubleshooting

### 502 Bad Gateway
- Check if app is running: `sudo systemctl status slayfashion`
- Check logs: `sudo journalctl -u slayfashion -n 50`

### Database Connection Failed
- Verify `DATABASE_URL` is correct
- Check PostgreSQL is running: `sudo systemctl status postgresql`
- Test connection: `psql $DATABASE_URL`

### OTP Not Sending
- Check Twilio credentials
- Verify Twilio phone number is verified
- Check Twilio account balance

### Slow Response Times
- Check database queries (add indexes)
- Enable caching (Redis)
- Scale horizontally

---

## Cost Comparison

| Platform | Basic | Production | Enterprise |
|----------|-------|------------|------------|
| **Railway** | $5/mo | $20/mo | $50/mo |
| **Heroku** | $7/mo | $25/mo | $250/mo |
| **DigitalOcean** | $12/mo | $24/mo | $48/mo |
| **AWS** | Free tier | $20/mo | $100+/mo |

**Recommendation**: Start with **Railway** ($5/mo) - easiest and cheapest!

---

## Support

Need help? Check:
- Main README.md
- SETUP.md
- ARCHITECTURE.md
- GitHub Issues

---

Happy deploying! 🚀

