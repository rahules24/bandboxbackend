# WhatsApp Webhook Quick Reference 🚀

## Environment Variables Needed

```bash
# Add to your .env file:
WHATSAPP_WEBHOOK_VERIFY_TOKEN=YourCustomToken123
WHATSAPP_APP_SECRET=your_facebook_app_secret
```

## Setup Commands

```bash
# 1. Run migrations
python manage.py makemigrations whatsapp
python manage.py migrate

# 2. Create superuser (if needed)
python manage.py createsuperuser

# 3. Deploy
fly deploy

# OR for local testing with ngrok:
ngrok http 8000
```

## Webhook Configuration

**Meta Developer Console:**
1. Go to: https://developers.facebook.com/apps/ → Your App → WhatsApp → Configuration
2. Callback URL: `https://your-app.fly.dev/api/whatsapp/webhook/`
3. Verify Token: Same as `WHATSAPP_WEBHOOK_VERIFY_TOKEN` in .env
4. Subscribe to fields: `messages` and `message_status`

## View Messages

### Django Admin (Easiest)
```
URL: https://your-app.fly.dev/admin/whatsapp/whatsappmessage/
```

### API Endpoints
```bash
# All messages
GET /api/whatsapp/messages/

# Filter by phone
GET /api/whatsapp/messages/?phone=919876543210

# All conversations
GET /api/whatsapp/conversations/

# Mark as read
POST /api/whatsapp/mark-read/
Body: {"phone_number": "919876543210"}
```

## Testing

```bash
# 1. Send a WhatsApp message TO your WABA number
#    (from your personal WhatsApp)

# 2. Check logs
fly logs

# 3. View in admin panel
https://your-app.fly.dev/admin/

# 4. Or query API
curl https://your-app.fly.dev/api/whatsapp/messages/
```

## Important Notes

### ❌ Cannot Use WhatsApp Business App
- Your WABA API number **cannot** be used with the mobile WhatsApp Business app
- It's either API OR mobile app - not both
- This is a WhatsApp limitation

### 📞 Calls Not Supported
- WABA API doesn't support voice/video calls
- Customers will see "This business account can't receive calls"
- **Solution:** Display a separate phone number for calls in your business profile

### 🔐 Security
- Webhook must use HTTPS
- Signature verification is enabled by default
- Never commit tokens to Git

## Troubleshooting

### Webhook verification fails:
- Check that `WHATSAPP_WEBHOOK_VERIFY_TOKEN` matches in both .env and Meta Console
- Ensure URL is publicly accessible (HTTPS)

### Messages not appearing:
- Check `fly logs` for errors
- Verify webhook is subscribed to "messages" field
- Test webhook verification endpoint

### Database empty:
- Run migrations: `python manage.py migrate`
- Check if `whatsapp` is in `INSTALLED_APPS`

## File Structure

```
bandboxbackend/
  whatsapp/
    __init__.py
    admin.py          ← Django admin interface for messages
    apps.py
    models.py         ← Database models (Messages, Status, Conversations)
    serializers.py    ← REST API serializers
    urls.py           ← URL routes
    views.py          ← Webhook handler + API views
    SETUP_GUIDE.md    ← Detailed setup instructions
```

## Common Use Cases

### Send auto-reply when message received:
Edit `whatsapp/views.py` → `_handle_messages()` method

### Link messages to your customer database:
Edit `whatsapp/views.py` → Add logic to match `from_number` with your Bill/Customer models

### Notify staff of new messages:
Edit `whatsapp/views.py` → `_handle_messages()` → Add email/SMS notification

### Download media files:
Already implemented! Check `_download_media()` method

## Next Steps

1. ✅ Set up webhook (follow SETUP_GUIDE.md)
2. ✅ Test receiving messages
3. 🔧 Customize auto-reply logic
4. 🎨 Build custom frontend (optional)
5. 🤖 Add AI-powered responses (optional)

---

For detailed instructions, see **SETUP_GUIDE.md**
