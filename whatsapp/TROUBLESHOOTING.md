# 🔧 Troubleshooting Guide - WhatsApp Webhooks

## Common Issues and Solutions

### 🚫 Webhook Verification Failed

**Symptom:** Meta Developer Console shows "Invalid" or "Verification Failed" when setting up webhook

**Possible Causes:**

1. **Verify token mismatch**
   ```
   ❌ Problem: Token in Meta Console ≠ Token in .env file
   
   ✅ Solution:
   - Check .env file: WHATSAPP_WEBHOOK_VERIFY_TOKEN=YourToken
   - Check Meta Console webhook settings
   - Make sure they EXACTLY match (case-sensitive!)
   ```

2. **Backend not accessible**
   ```
   ❌ Problem: Webhook URL not publicly reachable
   
   ✅ Solution:
   - Test URL in browser: https://your-app.fly.dev/api/whatsapp/webhook/
   - For local dev, use ngrok: ngrok http 8000
   - Make sure fly.io app is deployed and running
   ```

3. **Wrong endpoint URL**
   ```
   ❌ Wrong: https://your-app.fly.dev/whatsapp/webhook/
   ❌ Wrong: https://your-app.fly.dev/api/webhook/
   
   ✅ Correct: https://your-app.fly.dev/api/whatsapp/webhook/
   ```

4. **HTTPS required**
   ```
   ❌ Wrong: http://your-app.fly.dev/api/whatsapp/webhook/
   
   ✅ Correct: https://your-app.fly.dev/api/whatsapp/webhook/
   
   Note: Facebook requires HTTPS for webhooks
   ```

**How to test manually:**
```bash
# This simulates Facebook's verification request
curl "https://your-app.fly.dev/api/whatsapp/webhook/?hub.mode=subscribe&hub.challenge=12345&hub.verify_token=YourToken"

# Should return: 12345
```

---

### 📭 Not Receiving Messages

**Symptom:** Webhook is verified but messages don't appear in database

**Possible Causes:**

1. **Webhook fields not subscribed**
   ```
   ✅ Solution:
   Meta Developer Console > WhatsApp > Configuration
   Check that you've subscribed to:
   - messages ✓
   - message_status ✓
   ```

2. **Migrations not run**
   ```
   ❌ Problem: Database tables don't exist
   
   ✅ Solution:
   python manage.py makemigrations whatsapp
   python manage.py migrate
   
   # Verify tables exist:
   python manage.py dbshell
   \dt whatsapp_*
   ```

3. **App not in INSTALLED_APPS**
   ```
   ❌ Problem: 'whatsapp' not in settings.py
   
   ✅ Solution:
   Check bbdBackend/settings.py:
   
   INSTALLED_APPS = [
       ...
       "whatsapp",  # ← Make sure this exists
       ...
   ]
   ```

4. **Sending to wrong number**
   ```
   ❌ Problem: Sending FROM your WABA number instead of TO it
   
   ✅ Solution:
   - Use your personal WhatsApp
   - Send message TO your business number
   - Don't use the same number to send and receive
   ```

**How to debug:**
```bash
# Check logs
fly logs --app your-app-name

# Look for:
✓ "Webhook verified successfully!"
✓ "Received webhook: {...}"
✓ "Saved message <id> from <phone>"

# If you see errors:
✗ "Invalid signature" → Check WHATSAPP_APP_SECRET
✗ "DoesNotExist" → Run migrations
✗ Nothing logged → Check webhook subscription
```

---

### 🔴 Messages Saved But Not in Admin Panel

**Symptom:** Database has messages but admin panel is empty

**Possible Causes:**

1. **Superuser not created**
   ```
   ✅ Solution:
   python manage.py createsuperuser
   ```

2. **Wrong admin URL**
   ```
   ❌ Wrong: https://your-app.fly.dev/whatsapp/admin/
   
   ✅ Correct: https://your-app.fly.dev/admin/whatsapp/whatsappmessage/
   ```

3. **Admin not registered**
   ```
   Check whatsapp/admin.py exists and contains:
   
   @admin.register(WhatsAppMessage)
   class WhatsAppMessageAdmin(admin.ModelAdmin):
       ...
   ```

**How to verify data exists:**
```bash
# Connect to database
fly postgres connect -a your-db-name

# Check messages
SELECT COUNT(*) FROM whatsapp_whatsappmessage;

# View recent messages
SELECT from_number, text_body, timestamp 
FROM whatsapp_whatsappmessage 
ORDER BY timestamp DESC 
LIMIT 5;
```

---

### 🔒 "Invalid Signature" Errors

**Symptom:** Logs show "Invalid webhook signature" or 403 Forbidden

**Possible Causes:**

1. **App Secret not configured**
   ```
   ✅ Solution:
   Add to .env:
   WHATSAPP_APP_SECRET=your_facebook_app_secret
   
   Get from:
   Meta Developer Console > Settings > Basic > App Secret
   ```

2. **Wrong App Secret**
   ```
   ✅ Solution:
   - Make sure you copied the full secret (no spaces)
   - It should be a long hexadecimal string
   - Click "Show" in Meta Console to reveal it
   ```

3. **Signature verification too strict**
   ```
   Temporary workaround for testing:
   
   In whatsapp/views.py, temporarily modify _verify_signature:
   
   def _verify_signature(self, request):
       return True  # ⚠️ ONLY for testing!
   
   Don't forget to restore proper verification later!
   ```

---

### 📞 "This business account can't receive calls"

**Symptom:** Customers see this message when trying to call

**Explanation:** This is **normal behavior** for WABA API numbers!

WhatsApp Business API does NOT support voice/video calls.

**Solutions:**

1. **Display alternative phone number**
   ```
   Set in WhatsApp Business Profile:
   Business Phone: +91 98765 43210 (for voice calls)
   
   Customers will see this when they try to call.
   ```

2. **Use separate number for calls**
   ```
   Strategy:
   - WABA Number (+91 11111): Messages only
   - Business Line (+91 22222): Voice calls only
   ```

3. **Auto-reply with call instructions**
   ```python
   # Add to whatsapp/views.py
   if 'call' in text_body.lower():
       send_template_message(
           to=from_number,
           template='call_instructions',
           parameters=['Your call number: +91 98765 43210']
       )
   ```

---

### 🔄 Duplicate Messages

**Symptom:** Same message appears multiple times in database

**Possible Causes:**

1. **Duplicate prevention not working**
   ```
   Check whatsapp/views.py:
   
   # This should exist:
   if WhatsAppMessage.objects.filter(message_id=message_id).exists():
       logger.info(f'Message {message_id} already processed')
       continue
   ```

2. **Facebook retrying webhook**
   ```
   Explanation:
   - If your endpoint doesn't return 200 OK quickly
   - Facebook will retry sending the same message
   
   ✅ Solution:
   - Process messages asynchronously if needed
   - Always return 200 OK immediately
   ```

---

### 🖼️ Media Files Not Downloading

**Symptom:** Images/videos not accessible or URLs empty

**Possible Causes:**

1. **Access token expired**
   ```
   ✅ Solution:
   - Get new access token from Meta Developer Console
   - Update WHATSAPP_ACCESS_TOKEN in .env
   ```

2. **Media download fails**
   ```
   Check logs for:
   "Error downloading media: ..."
   
   Common issues:
   - Network timeout
   - Invalid access token
   - Media ID expired (WhatsApp deletes after 30 days)
   ```

3. **Need to store files**
   ```
   Current behavior: Stores media URL only
   
   To download and save files:
   
   In whatsapp/views.py, modify _download_media:
   
   # Save file to Django media folder
   import os
   from django.conf import settings
   
   file_path = os.path.join(settings.MEDIA_ROOT, f'{media_id}.jpg')
   with open(file_path, 'wb') as f:
       f.write(media_response.content)
   ```

---

### 🔌 Local Development Issues

**Symptom:** Webhook works in production but not locally

**Solutions:**

1. **Use ngrok for local testing**
   ```bash
   # Install ngrok: https://ngrok.com/download
   
   # Start Django
   python manage.py runserver
   
   # In another terminal, start ngrok
   ngrok http 8000
   
   # Use ngrok URL in Meta Console
   https://abc123.ngrok.io/api/whatsapp/webhook/
   ```

2. **CSRF issues**
   ```
   Webhook endpoint has @csrf_exempt decorator
   This is required for webhooks
   
   If you see CSRF errors, verify:
   @method_decorator(csrf_exempt, name='dispatch')
   class WhatsAppWebhookView(APIView):
       ...
   ```

3. **CORS issues**
   ```
   Webhooks don't need CORS
   But if you're testing from frontend:
   
   Add to settings.py:
   CORS_ALLOWED_ORIGINS = [
       "http://localhost:5173",  # Your frontend
   ]
   ```

---

### 🗄️ Database Connection Issues

**Symptom:** "Unable to connect to database" or "relation does not exist"

**Solutions:**

1. **Database not running**
   ```bash
   # For Fly.io PostgreSQL
   fly postgres connect -a your-db-name
   
   # Should connect without errors
   ```

2. **DATABASE_URL incorrect**
   ```
   Check .env:
   DATABASE_URL=postgres://user:pass@host:5432/dbname
   
   Format must be exact:
   postgres:// (or postgresql://)
   username:password
   @hostname:port
   /database_name
   ```

3. **Migrations not applied**
   ```bash
   # Check migration status
   python manage.py showmigrations whatsapp
   
   # Should show [X] for all migrations
   # If [ ] (empty), run:
   python manage.py migrate whatsapp
   ```

---

### ⚙️ Environment Variables Not Loading

**Symptom:** App can't find WHATSAPP_WEBHOOK_VERIFY_TOKEN or other variables

**Solutions:**

1. **For local development**
   ```
   Make sure .env file is in bandboxbackend/ directory
   
   bandboxbackend/
     .env          ← Here!
     manage.py
     ...
   ```

2. **For Fly.io production**
   ```bash
   # Set secrets
   fly secrets set WHATSAPP_WEBHOOK_VERIFY_TOKEN="YourToken" -a bandboxbackend
   fly secrets set WHATSAPP_APP_SECRET="YourSecret" -a bandboxbackend
   
   # Verify secrets
   fly secrets list -a bandboxbackend
   ```

3. **Variable name typo**
   ```
   Common mistakes:
   ❌ WHATSAPP_VERIFY_TOKEN
   ✅ WHATSAPP_WEBHOOK_VERIFY_TOKEN
   
   ❌ FACEBOOK_APP_SECRET
   ✅ WHATSAPP_APP_SECRET
   ```

---

## 🧪 Testing Checklist

When troubleshooting, go through this checklist:

### Environment Setup
- [ ] `.env` file exists with all required variables
- [ ] `whatsapp` in `INSTALLED_APPS`
- [ ] Migrations run: `python manage.py migrate`
- [ ] Superuser created: `python manage.py createsuperuser`

### Deployment
- [ ] App deployed and accessible via HTTPS
- [ ] Webhook URL correct: `/api/whatsapp/webhook/`
- [ ] Logs show no deployment errors

### Meta Configuration
- [ ] Webhook verified (green checkmark in Meta Console)
- [ ] Subscribed to `messages` field
- [ ] Subscribed to `message_status` field
- [ ] Access token is valid and not expired

### Testing
- [ ] Send test message TO your WABA number
- [ ] Check logs for "Received webhook" message
- [ ] Check database for new message
- [ ] Check admin panel for message

---

## 🔍 Debugging Commands

```bash
# Check if webhook endpoint is accessible
curl https://your-app.fly.dev/api/whatsapp/webhook/

# Test webhook verification
curl "https://your-app.fly.dev/api/whatsapp/webhook/?hub.mode=subscribe&hub.challenge=test123&hub.verify_token=YourToken"

# View logs
fly logs --app your-app-name

# Connect to database
fly postgres connect -a your-db-name

# Check messages in database
SELECT COUNT(*) FROM whatsapp_whatsappmessage;

# View recent messages
SELECT from_number, message_type, text_body, timestamp 
FROM whatsapp_whatsappmessage 
ORDER BY timestamp DESC 
LIMIT 10;

# Check migrations
python manage.py showmigrations whatsapp

# Test API endpoint
curl https://your-app.fly.dev/api/whatsapp/messages/

# Check environment variables (local)
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('WHATSAPP_WEBHOOK_VERIFY_TOKEN'))"

# Check environment variables (Fly.io)
fly secrets list -a your-app-name
```

---

## 📊 Understanding Webhook Payloads

### Successful Message Webhook:
```json
{
  "object": "whatsapp_business_account",
  "entry": [{
    "id": "WABA_ID",
    "changes": [{
      "value": {
        "messaging_product": "whatsapp",
        "metadata": {
          "display_phone_number": "15551234567",
          "phone_number_id": "PHONE_NUMBER_ID"
        },
        "contacts": [{
          "profile": {
            "name": "John Doe"
          },
          "wa_id": "919876543210"
        }],
        "messages": [{
          "from": "919876543210",
          "id": "wamid.HBgNMTU1...",
          "timestamp": "1704123456",
          "text": {
            "body": "Hello"
          },
          "type": "text"
        }]
      },
      "field": "messages"
    }]
  }]
}
```

### What Your Code Does:
1. ✅ Extracts `messages` array
2. ✅ Gets `from`, `id`, `timestamp`, `type`
3. ✅ Saves to `WhatsAppMessage` model
4. ✅ Updates `WhatsAppConversation`
5. ✅ Downloads media if present
6. ✅ Returns 200 OK

---

## 🆘 Still Having Issues?

### Check these files for clues:

1. **whatsapp/views.py**
   - Contains all webhook logic
   - Check `_verify_signature`, `_handle_messages`, `_handle_statuses`

2. **whatsapp/models.py**
   - Database structure
   - Verify field names match what you're saving

3. **bbdBackend/settings.py**
   - Ensure `whatsapp` in `INSTALLED_APPS`
   - Check database configuration

4. **logs**
   ```bash
   fly logs --app your-app-name
   ```
   - Most errors will appear here
   - Look for Python exceptions

### Enable verbose logging:

Add to `bbdBackend/settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'whatsapp': {  # ← Add this
            'handlers': ['console'],
            'level': 'DEBUG',  # ← Verbose logging
        },
    },
}
```

---

## 💡 Pro Tips

1. **Always check logs first** - Most issues show up there
2. **Test locally with ngrok** - Easier to debug than production
3. **Use Meta's webhook testing tool** - Sends test payloads
4. **Keep raw_payload** - The `raw_payload` field stores full webhook data for debugging
5. **Return 200 OK always** - Even on errors, to prevent Facebook from retrying
6. **Monitor database size** - Messages accumulate quickly; plan archiving strategy

---

**Still stuck?** 

1. Check the SETUP_GUIDE.md for step-by-step instructions
2. Review ARCHITECTURE.md to understand the flow
3. Look at the code comments in whatsapp/views.py
4. Test with the debugging commands above

Good luck! 🚀
