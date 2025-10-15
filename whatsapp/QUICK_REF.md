# ⚡ Quick Reference Card

## 🔧 Setup (One-time)

```bash
# 1. Add to .env
WHATSAPP_WEBHOOK_VERIFY_TOKEN=YourCustomToken
WHATSAPP_APP_SECRET=your_facebook_app_secret

# 2. Run migrations
python manage.py makemigrations whatsapp
python manage.py migrate

# 3. Deploy
fly deploy

# 4. Configure in Meta Console
# URL: https://your-app.fly.dev/api/whatsapp/webhook/
# Token: Same as WHATSAPP_WEBHOOK_VERIFY_TOKEN
# Subscribe: messages, message_status
```

## 👀 View Messages

```bash
# Admin Panel
https://your-app.fly.dev/admin/whatsapp/whatsappmessage/

# API
GET /api/whatsapp/messages/
GET /api/whatsapp/messages/?phone=919876543210
GET /api/whatsapp/conversations/

# Database
SELECT * FROM whatsapp_whatsappmessage ORDER BY timestamp DESC;
```

## 🔍 Debug

```bash
# Logs
fly logs

# Test webhook
curl "https://your-app.fly.dev/api/whatsapp/webhook/?hub.mode=subscribe&hub.challenge=123&hub.verify_token=YourToken"

# Check DB
fly postgres connect -a your-db
SELECT COUNT(*) FROM whatsapp_whatsappmessage;
```

## ❓ Common Issues

| Problem | Solution |
|---------|----------|
| Webhook verification fails | Check token matches in .env and Meta Console |
| Messages not appearing | Check logs, verify webhook subscription |
| Can't receive calls | Normal for WABA - use separate phone number |
| Media not downloading | Check WHATSAPP_ACCESS_TOKEN is valid |

## 📁 Files

| File | Purpose |
|------|---------|
| START_HERE.md | Complete overview (read first!) |
| SETUP_GUIDE.md | Step-by-step setup instructions |
| README.md | Quick commands reference |
| ARCHITECTURE.md | Visual diagrams |
| TROUBLESHOOTING.md | Problem solutions |

## 🎯 Endpoints

```
POST /api/whatsapp/webhook/         ← Facebook sends here
GET  /api/whatsapp/webhook/         ← Verification
GET  /api/whatsapp/messages/        ← View messages
GET  /api/whatsapp/conversations/   ← View conversations
POST /api/whatsapp/mark-read/       ← Mark as read
```

## 💾 Models

```python
WhatsAppMessage         # Incoming messages
WhatsAppMessageStatus   # Delivery receipts
WhatsAppConversation    # Grouped by customer
```

## 🔐 Security

```
✓ HTTPS required
✓ Signature verification
✓ Environment variables
✓ CSRF exempt (webhooks only)
```

---

**Need help?** Read START_HERE.md or TROUBLESHOOTING.md
