# 🎉 Getting Started with SlayFashion Backend

Welcome! This guide will get you up and running in **5 minutes**.

## 📋 What You're Building

A **FastAPI backend** that enables **OTP-based login** for Shopify customers - just like **GoKwik** and **KwikPass**!

### How It Works

```
Customer enters phone → Receives OTP → Verifies OTP → Logged into Shopify! ✨
```

No passwords needed! The backend handles everything automatically using the **"bridge method"**.

---

## 🚀 Quick Setup (5 Minutes)

### Step 1: Install Dependencies (2 min)

```bash
cd /Users/granth/Desktop/slayfashionbackend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### Step 2: Get Shopify Admin API Token (2 min)

This is the **only required setup** to get started!

1. Open: https://f3lifestyle.myshopify.com/admin/settings/apps/development
2. Click **"Create an app"**
3. Name: "SlayFashion Backend"
4. Go to **"Configuration"** → **"Admin API integration"**
5. Select scopes:
   - ✅ `read_customers`
   - ✅ `write_customers`
6. Click **"Save"** then **"Install app"**
7. Copy the **Admin API access token** (starts with `shpat_`)

### Step 3: Update Configuration (30 sec)

Open `.env` file and update this line:

```bash
SHOPIFY_ADMIN_API_TOKEN=shpat_xxxxxxxxxxxxx  # ← Paste your token here
```

That's it! Everything else is optional for now.

### Step 4: Run! (30 sec)

```bash
python run.py
```

You should see:

```
============================================================
🚀 SlayFashion Backend API
============================================================
📍 Host: 0.0.0.0
🔌 Port: 8000
📦 Shopify Store: f3lifestyle.myshopify.com
📚 API Docs: http://0.0.0.0:8000/docs
============================================================
INFO:     Uvicorn running on http://0.0.0.0:8000
```

🎉 **Your backend is running!**

---

## 🧪 Test It Out

### Option 1: Using Browser (Easiest)

1. Open: **http://localhost:8000/docs**
2. You'll see the interactive API documentation (Swagger UI)

**Send OTP:**
1. Find `POST /api/auth/send-otp`
2. Click **"Try it out"**
3. Enter phone number:
   ```json
   {
     "phone": "+919876543210"
   }
   ```
4. Click **"Execute"**
5. Copy the `session_id` from response

**Check Console for OTP:**
Since Twilio isn't configured yet, the backend runs in **dev mode** and prints the OTP to the console. Look at your terminal:

```
⚠️ DEV MODE: OTP not sent but proceeding. OTP is: 123456
```

**Verify OTP:**
1. Find `POST /api/auth/verify-otp`
2. Click **"Try it out"**
3. Enter:
   ```json
   {
     "phone": "+919876543210",
     "otp": "123456",
     "session_id": "paste_session_id_here"
   }
   ```
4. Click **"Execute"**

You'll get back:
```json
{
  "success": true,
  "message": "Login successful",
  "customer": {
    "id": "1",
    "phone": "+919876543210",
    "shopify_customer_id": "gid://shopify/Customer/..."
  },
  "access_token": "eyJhbGci...",
  "token_expires_at": "2025-11-19T12:00:00Z"
}
```

🎊 **It works!** A customer was created in Shopify and you got an access token!

### Option 2: Using Test Script

```bash
python test_api.py
```

### Option 3: Using cURL

```bash
# Send OTP
curl -X POST http://localhost:8000/api/auth/send-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919876543210"}'

# Verify OTP (use session_id from above response)
curl -X POST http://localhost:8000/api/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+919876543210",
    "otp": "123456",
    "session_id": "your_session_id_here"
  }'
```

---

## 📱 Integrate with Your React Native App

Now that the backend works, let's connect it to your mobile app!

### Update Backend URL

In your React Native app (`SLAYFASHIONAPP`), create or update this file:

```typescript
// src/config/backend.ts
import { Platform } from 'react-native';

export const BACKEND_CONFIG = {
  apiUrl: Platform.OS === 'android' 
    ? 'http://10.0.2.2:8000'     // Android emulator
    : 'http://localhost:8000',   // iOS simulator
};

// For physical device, use your computer's IP:
// apiUrl: 'http://192.168.1.100:8000'  // Replace with your IP
```

### Add Auth Service

Create `src/services/authService.ts`:

```typescript
import axios from 'axios';
import { BACKEND_CONFIG } from '../config/backend';

const api = axios.create({
  baseURL: BACKEND_CONFIG.apiUrl,
  timeout: 15000,
});

export async function sendOTP(phone: string) {
  const response = await api.post('/api/auth/send-otp', { phone });
  return response.data;
}

export async function verifyOTP(phone: string, otp: string, sessionId: string) {
  const response = await api.post('/api/auth/verify-otp', {
    phone,
    otp,
    session_id: sessionId,
  });
  return response.data;
}
```

See **INTEGRATION.md** for complete frontend integration guide with full LoginScreen example!

---

## 📚 Documentation

Your backend comes with comprehensive documentation:

| File | Description |
|------|-------------|
| **QUICKSTART.md** | 5-minute quick start guide |
| **README.md** | Complete documentation |
| **SETUP.md** | Detailed setup instructions |
| **INTEGRATION.md** | Frontend integration guide |
| **ARCHITECTURE.md** | System architecture & flow diagrams |
| **DEPLOYMENT.md** | Production deployment guides |

---

## 🔧 Optional: Enable Real SMS

Right now, OTP codes are printed to the console (dev mode). To send real SMS:

### Step 1: Sign up for Twilio

1. Go to https://www.twilio.com
2. Create free account (get $15 credit!)
3. Get a phone number
4. Copy your credentials from dashboard

### Step 2: Update .env

```bash
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890
```

### Step 3: Restart Backend

```bash
python run.py
```

Now OTPs will be sent via SMS! 📱

---

## 🚀 Next Steps

### For Development

- ✅ Backend is running locally
- ✅ Test API with Swagger UI
- ✅ Integrate with React Native app
- 📖 Read INTEGRATION.md for frontend code

### For Production

- 🌐 Deploy to Railway/Heroku (see DEPLOYMENT.md)
- 🔒 Setup PostgreSQL database
- 📱 Enable real SMS with Twilio
- 🔐 Configure HTTPS/SSL
- 📊 Add monitoring (Sentry, UptimeRobot)

---

## 🎯 What You Can Do Now

With your access token, the mobile app can:

✅ **Fetch customer orders** from Shopify
✅ **Get customer profile** information
✅ **Create checkouts** for purchases
✅ **Manage addresses** and preferences
✅ **View order history** and tracking

All without the customer ever seeing a password! 🎉

---

## 🆘 Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt --force-reinstall
```

### Port 8000 already in use
```bash
# Change port in .env
PORT=8001
```

### Shopify API errors
- Make sure `SHOPIFY_ADMIN_API_TOKEN` is correct (starts with `shpat_`)
- Verify API scopes include `read_customers` and `write_customers`
- Check store domain is correct (no `https://`)

### Can't connect from mobile app
- **Android emulator**: Use `http://10.0.2.2:8000`
- **iOS simulator**: Use `http://localhost:8000`
- **Physical device**: Use your computer's IP (find with `ipconfig` on Windows or `ifconfig` on Mac/Linux)

---

## 🎓 Learning Resources

### Understanding the System

1. Read **ARCHITECTURE.md** - See how everything connects
2. Watch API Docs - http://localhost:8000/docs
3. Check logs - See what happens when you make requests

### API Endpoints

- `POST /api/auth/send-otp` - Send OTP to phone
- `POST /api/auth/verify-otp` - Verify OTP & login
- `GET /api/customer/profile` - Get customer info
- `GET /health` - Check if server is running

---

## ✨ Features

✅ **OTP-based authentication** - No passwords needed
✅ **Shopify integration** - Automatic customer creation
✅ **Rate limiting** - Prevent abuse
✅ **Token-based auth** - Secure access tokens
✅ **Hidden credentials** - Bridge method for Shopify
✅ **Development mode** - Console OTP for testing
✅ **Production ready** - Easy deployment
✅ **Well documented** - Comprehensive guides
✅ **Type safe** - Pydantic validation
✅ **Modern stack** - FastAPI + SQLAlchemy

---

## 🤝 Need Help?

1. Check the documentation files
2. Look at the Swagger UI (http://localhost:8000/docs)
3. Review the architecture diagram (ARCHITECTURE.md)
4. Test with the provided test script (`test_api.py`)

---

## 🎊 You're All Set!

You now have a production-ready FastAPI backend that enables OTP-based login for Shopify - just like the big players (GoKwik, KwikPass)!

**What to do next:**
1. ✅ Test the API (you just did!)
2. 📱 Integrate with your React Native app (see INTEGRATION.md)
3. 🚀 Deploy to production when ready (see DEPLOYMENT.md)

Happy coding! 🚀

---

Made with ❤️ for SlayFashion

