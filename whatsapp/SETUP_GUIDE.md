# WhatsApp Webhook Setup Guide 📱

## Overview
This guide explains how to set up webhooks to receive incoming WhatsApp messages through Facebook's Graph API (WABA - WhatsApp Business API).

## 🎯 What You'll Achieve
- ✅ Receive incoming WhatsApp messages in your Django backend
- ✅ Store messages in your database
- ✅ View messages through Django Admin panel
- ✅ Track message delivery statuses
- ✅ Manage conversations programmatically

---

## 📋 Prerequisites

1. **WhatsApp Business Account** - You already have this (since you're sending messages)
2. **Meta Developer Account** - Already set up
3. **Publicly accessible URL** - Your backend must be accessible from the internet
   - For production: Your fly.io URL (e.g., `https://your-app.fly.dev`)
   - For development: Use ngrok or similar tunneling service

---

## 🚀 Step-by-Step Setup

### Step 1: Update Environment Variables

Add these to your `.env` file:

```bash
# Your existing WhatsApp credentials
WHATSAPP_ACCESS_TOKEN=your_existing_token
WHATSAPP_PHONE_NUMBER_ID=your_existing_phone_id
WHATSAPP_RECIPIENT_NUMBER=your_number

# NEW: Webhook credentials
WHATSAPP_WEBHOOK_VERIFY_TOKEN=MyCustomSecureToken123!
WHATSAPP_APP_SECRET=your_facebook_app_secret
```

**How to get these:**

1. **WHATSAPP_WEBHOOK_VERIFY_TOKEN**: 
   - Create your own random string (e.g., "MyApp_Webhook_2024_SecureToken")
   - This is used to verify your webhook endpoint
   - Keep it secret and make it unique

2. **WHATSAPP_APP_SECRET**:
   - Go to https://developers.facebook.com/apps/
   - Select your app
   - Go to **Settings** > **Basic**
   - Copy the **App Secret** (click "Show")

### Step 2: Run Database Migrations

```bash
# Create migration files for the new whatsapp app
python manage.py makemigrations whatsapp

# Apply migrations to create database tables
python manage.py migrate
```

This creates 3 tables:
- `whatsapp_whatsappmessage` - Stores incoming messages
- `whatsapp_whatsappmessagestatus` - Tracks message delivery statuses
- `whatsapp_whatsappconversation` - Groups messages by phone number

### Step 3: Deploy Your Backend

Your webhook URL must be publicly accessible. Options:

**Production (Fly.io):**
```bash
fly deploy
```

**Development (using ngrok):**
```bash
# Install ngrok: https://ngrok.com/download
ngrok http 8000

# This gives you a URL like: https://abc123.ngrok.io
```

### Step 4: Configure Webhook in Meta Developer Console

1. **Go to Meta Developer Console:**
   - Visit https://developers.facebook.com/apps/
   - Select your app
   - In the left sidebar, find **WhatsApp** > **Configuration**

2. **Configure Webhook:**
   
   Click on **Edit** or **Configure Webhooks**
   
   **Callback URL:** Enter your webhook endpoint
   ```
   Production: https://your-app.fly.dev/api/whatsapp/webhook/
   Dev: https://abc123.ngrok.io/api/whatsapp/webhook/
   ```
   
   **Verify Token:** Enter the SAME token from your `.env` file
   ```
   MyCustomSecureToken123!
   ```
   
   Click **Verify and Save**
   
   ✅ You should see "Valid" or "Verified" status

3. **Subscribe to Webhook Fields:**
   
   After verification, you need to subscribe to events:
   
   ✅ Check these fields:
   - `messages` - To receive incoming messages
   - `message_status` - To get delivery/read receipts
   
   Click **Subscribe**

### Step 5: Test the Webhook

1. **Send a message TO your WhatsApp Business number:**
   - Use your personal WhatsApp
   - Send a message to your WABA number (not FROM it, TO it)
   - Example: "Hello, I need help with my order"

2. **Check if it's received:**
   
   **Option A: Django Admin Panel**
   ```
   Visit: http://your-app.fly.dev/admin/
   Login with your superuser credentials
   Go to: WHATSAPP > WhatsApp messages
   ```
   You should see the message there!

   **Option B: API Endpoint**
   ```bash
   curl http://your-app.fly.dev/api/whatsapp/messages/
   ```

   **Option C: Check Logs**
   ```bash
   # Fly.io
   fly logs
   
   # Local
   python manage.py runserver
   # Watch for: "Saved message <id> from <phone>"
   ```

---

## 🖥️ Where to See Incoming Messages

### 1. **Django Admin Panel** (Recommended for viewing)

**URL:** `https://your-app.fly.dev/admin/whatsapp/whatsappmessage/`

**Features:**
- View all messages in a table
- Filter by date, message type, sender
- Search by phone number or content
- See full message details including media

**Create a superuser if you don't have one:**
```bash
python manage.py createsuperuser
```

### 2. **REST API Endpoints**

**Get all messages:**
```bash
GET /api/whatsapp/messages/

# Filter by phone
GET /api/whatsapp/messages/?phone=919876543210

# Filter by type
GET /api/whatsapp/messages/?type=text

# Limit results
GET /api/whatsapp/messages/?limit=50
```

**Get conversations:**
```bash
GET /api/whatsapp/conversations/
```

**Mark as read:**
```bash
POST /api/whatsapp/mark-read/
Body: {"phone_number": "919876543210"}
```

### 3. **Database Directly**

```sql
-- View recent messages
SELECT from_number, from_name, text_body, timestamp 
FROM whatsapp_whatsappmessage 
ORDER BY timestamp DESC 
LIMIT 10;

-- View conversations
SELECT phone_number, contact_name, message_count, unread_count
FROM whatsapp_whatsappconversation
ORDER BY last_message_at DESC;
```

---

## ❓ Does WhatsApp Provide a UI to See Messages?

### Meta Business Suite (Limited)

**URL:** https://business.facebook.com/

**What you can see:**
- ✅ Message thread history
- ✅ Basic conversation view
- ✅ Send/receive messages manually

**Limitations:**
- ❌ Not suitable for programmatic access
- ❌ No API integration
- ❌ Can't process messages automatically
- ❌ Manual interaction only

**Best for:** Human agents responding to customers

### WhatsApp Business App (NOT for API numbers!)

⚠️ **IMPORTANT:** You **CANNOT** use the regular WhatsApp Business app on your phone with a WABA API number!

**Why?**
- When you use the WhatsApp Business API (WABA), the number is "reserved" for API use only
- You can't log into that number with the mobile app
- It's either API **OR** mobile app - not both!

**The tradeoff:**
- 📱 WhatsApp Business App: Easy to use, mobile interface, but limited to 4 devices
- 🤖 WABA API: Unlimited automation, no mobile app, requires custom interface

---

## 📞 How to Manage Calls

### Problem: WABA API Doesn't Handle Voice/Video Calls

**WhatsApp Business API does NOT support:**
- ❌ Voice calls
- ❌ Video calls
- ❌ Call notifications via webhook

### Solutions:

#### Option 1: Display Alternative Contact Methods
When customers try to call, they'll see "This business account can't receive calls."

In your WhatsApp Business Profile, set up:
```
Business Phone: +91 98765 43210 (for calls)
Business Email: support@bandboxdrycleaners.com
```

#### Option 2: Auto-Reply with Call Instructions

Add this to your webhook handler to detect when someone might want to call:

```python
# In whatsapp/views.py - _handle_messages method
if 'call' in text_body.lower() or 'phone' in text_body.lower():
    # Send auto-reply with call number
    send_template_message(
        to=from_number,
        template='call_instructions',
        parameters=['Your business call number here']
    )
```

#### Option 3: Use a Separate Number for Calls

**Recommended Setup:**
- **WABA API Number:** For automated messages only (WhatsApp only)
- **Business Phone:** Regular phone line for voice calls
- **Display both** in your business profile and website

Example:
```
WhatsApp: +91 98765 11111 (Messages only)
Call us: +91 98765 22222 (Voice calls)
```

#### Option 4: Use Click-to-Call Links

In your website/app, provide a button:
```html
<a href="tel:+919876543210">📞 Call Us</a>
```

This bypasses WhatsApp entirely for calls.

---

## 🔐 Security Best Practices

### 1. Verify Webhook Signatures

The code includes signature verification using your App Secret. This ensures requests actually come from Facebook.

```python
def _verify_signature(self, request):
    signature = request.META.get('HTTP_X_HUB_SIGNATURE_256', '')
    # Verifies using your WHATSAPP_APP_SECRET
```

### 2. Protect Your Endpoints

The webhook endpoint (`/api/whatsapp/webhook/`) should:
- ✅ Be HTTPS only (enforced by Facebook)
- ✅ Verify signatures
- ✅ Log suspicious activity

### 3. Environment Variables

Never commit these to Git:
- `WHATSAPP_ACCESS_TOKEN`
- `WHATSAPP_APP_SECRET`
- `WHATSAPP_WEBHOOK_VERIFY_TOKEN`

---

## 🧪 Testing Webhooks

### Test Message Flow:

1. **Send a test message TO your WABA number** from your personal WhatsApp
2. **Check webhook receives it:**
   ```bash
   fly logs --app your-app-name
   # Look for: "Saved message <id> from <phone>"
   ```

3. **View in admin panel:**
   ```
   https://your-app.fly.dev/admin/whatsapp/whatsappmessage/
   ```

### Test Different Message Types:

Send these to your WABA number:

- ✅ **Text:** "Hello, this is a test"
- ✅ **Image:** Send any photo
- ✅ **Location:** Share your location
- ✅ **Document:** Send a PDF/doc
- ✅ **Reply:** Reply to a message your bot sent

All should appear in your database!

---

## 📊 Message Types Supported

The webhook handles:

| Type | Description | Stored Data |
|------|-------------|-------------|
| `text` | Plain text messages | `text_body` |
| `image` | Photos, JPG, PNG | `media_id`, `media_url`, `caption` |
| `video` | Video files | `media_id`, `media_url` |
| `audio` | Voice messages, audio | `media_id` |
| `document` | PDF, DOC, etc. | `media_id`, `media_url` |
| `location` | Shared location | `latitude`, `longitude` |
| `interactive` | Button/list replies | `text_body` |

---

## 🔄 Message Status Updates

When you SEND messages, you'll receive status updates:

- ✅ `sent` - Message sent from your server
- ✅ `delivered` - Message delivered to recipient's phone
- ✅ `read` - Recipient opened/read the message
- ❌ `failed` - Message failed (with error code)

These are stored in `WhatsAppMessageStatus` model.

---

## 🚨 Troubleshooting

### Webhook Not Receiving Messages

**1. Check webhook verification:**
```
Meta Developer Console > WhatsApp > Configuration
Status should be "Valid" or "Verified"
```

**2. Check subscriptions:**
```
Ensure you've subscribed to "messages" field
```

**3. Test webhook manually:**
```bash
# This simulates Facebook's verification
curl "https://your-app.fly.dev/api/whatsapp/webhook/?hub.mode=subscribe&hub.challenge=123&hub.verify_token=YourToken"

# Should return: 123
```

**4. Check logs:**
```bash
fly logs --app your-app-name

# Look for errors in webhook processing
```

### Messages Not Showing in Admin

**1. Check database:**
```bash
fly postgres connect -a your-db-name

SELECT COUNT(*) FROM whatsapp_whatsappmessage;
```

**2. Check migrations:**
```bash
python manage.py showmigrations whatsapp
# All should have [X]
```

### "This business account can't receive calls"

This is **normal** for WABA API numbers! See the "Managing Calls" section above.

---

## 🎨 Custom Frontend (Optional)

You can build a custom UI to display messages using the API endpoints:

```javascript
// Fetch conversations
const conversations = await fetch('/api/whatsapp/conversations/')
  .then(r => r.json());

// Fetch messages for specific conversation
const messages = await fetch('/api/whatsapp/messages/?phone=919876543210')
  .then(r => r.json());

// Mark as read
await fetch('/api/whatsapp/mark-read/', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({phone_number: '919876543210'})
});
```

---

## 📈 Next Steps

### 1. Auto-Reply Logic

Add automatic responses in `whatsapp/views.py`:

```python
def _send_auto_reply(self, to_number, message_type):
    # Send acknowledgment
    send_whatsapp_message(
        to=to_number,
        template='message_received',
        parameters=['We received your message!']
    )
```

### 2. Integration with Your Business Logic

Link messages to bills/customers:

```python
# In _handle_messages
phone_matches_bill = Bill.objects.filter(phone=from_number)
if phone_matches_bill.exists():
    # Update bill status, send tracking info, etc.
```

### 3. Notifications

Send notifications when new messages arrive:
- Email notifications
- SMS alerts
- Push notifications to your staff

### 4. AI-Powered Responses

Integrate with AI to auto-respond:
- ChatGPT for customer support
- Automated order status updates
- FAQ responses

---

## 📚 Resources

- **Meta Webhook Documentation:** https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks
- **WhatsApp Cloud API:** https://developers.facebook.com/docs/whatsapp/cloud-api
- **Message Types:** https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks/components

---

## ✅ Quick Checklist

- [ ] Add `whatsapp` to `INSTALLED_APPS`
- [ ] Add webhook environment variables to `.env`
- [ ] Run migrations: `python manage.py migrate`
- [ ] Deploy backend (must be publicly accessible)
- [ ] Configure webhook in Meta Developer Console
- [ ] Subscribe to `messages` and `message_status` fields
- [ ] Test by sending message to your WABA number
- [ ] Check Django admin to see messages
- [ ] Set up auto-reply logic (optional)
- [ ] Build custom UI (optional)

---

## 💡 Pro Tips

1. **Test in development first** - Use ngrok to test webhooks before deploying
2. **Log everything** - The `raw_payload` field stores complete webhook data for debugging
3. **Handle duplicates** - The code checks for duplicate `message_id` to prevent re-processing
4. **Media downloads** - Media files are downloaded automatically and URLs stored
5. **Conversations** - Use `WhatsAppConversation` to group messages by customer
6. **Status tracking** - Monitor message delivery with `WhatsAppMessageStatus`

---

**Need help?** Check the code comments in `whatsapp/views.py` for detailed explanations!
