# WhatsApp Integration Architecture

## Message Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     INCOMING MESSAGE FLOW                        │
└─────────────────────────────────────────────────────────────────┘

1. Customer sends WhatsApp message
   ┌──────────────┐
   │   Customer   │ "Hi, I need help with my order"
   │  📱 Mobile   │
   └──────┬───────┘
          │
          ▼
   ┌──────────────────┐
   │  WhatsApp Cloud  │ (Meta's infrastructure)
   └──────┬───────────┘
          │
          │ POST /api/whatsapp/webhook/
          │ {
          │   "object": "whatsapp_business_account",
          │   "entry": [{
          │     "changes": [{
          │       "value": {
          │         "messages": [{
          │           "from": "919876543210",
          │           "type": "text",
          │           "text": {"body": "Hi, I need help..."}
          │         }]
          │       }
          │     }]
          │   }]
          │ }
          ▼
   ┌─────────────────────────────────────────────────────────┐
   │         Your Django Backend (Fly.io/Railway)            │
   │                                                           │
   │  ┌─────────────────────────────────────────────────┐    │
   │  │  whatsapp/views.py                               │    │
   │  │  WhatsAppWebhookView                             │    │
   │  │                                                   │    │
   │  │  1. Verify signature ✓                           │    │
   │  │  2. Parse webhook payload                        │    │
   │  │  3. Extract message data                         │    │
   │  │  4. Save to database ──────────────┐             │    │
   │  │  5. Update conversation            │             │    │
   │  │  6. Download media (if any)        │             │    │
   │  │  7. Send auto-reply (optional)     │             │    │
   │  └────────────────────────────────────┼─────────────┘    │
   │                                       │                   │
   │  ┌────────────────────────────────────▼──────────────┐   │
   │  │  PostgreSQL Database                              │   │
   │  │                                                    │   │
   │  │  ┌──────────────────────────────────────────┐     │   │
   │  │  │  whatsapp_whatsappmessage               │     │   │
   │  │  │  ─────────────────────────────────────   │     │   │
   │  │  │  • message_id: "wamid.ABC123..."        │     │   │
   │  │  │  • from_number: "919876543210"          │     │   │
   │  │  │  • from_name: "John Doe"                │     │   │
   │  │  │  • text_body: "Hi, I need help..."      │     │   │
   │  │  │  • message_type: "text"                 │     │   │
   │  │  │  • timestamp: 2024-01-15 10:30:00       │     │   │
   │  │  │  • status: "received"                   │     │   │
   │  │  └──────────────────────────────────────────┘     │   │
   │  │                                                    │   │
   │  │  ┌──────────────────────────────────────────┐     │   │
   │  │  │  whatsapp_whatsappconversation          │     │   │
   │  │  │  ─────────────────────────────────────   │     │   │
   │  │  │  • phone_number: "919876543210"         │     │   │
   │  │  │  • contact_name: "John Doe"             │     │   │
   │  │  │  • message_count: 15                    │     │   │
   │  │  │  • unread_count: 3                      │     │   │
   │  │  │  • last_message_at: 2024-01-15 10:30:00 │     │   │
   │  │  └──────────────────────────────────────────┘     │   │
   │  └────────────────────────────────────────────────────┘   │
   └─────────────────────────────────────────────────────────────┘
                          │
                          │ View messages via:
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
   ┌──────────┐    ┌──────────┐   ┌──────────┐
   │  Django  │    │   REST   │   │ Database │
   │  Admin   │    │   API    │   │  Direct  │
   │  Panel   │    │          │   │          │
   └──────────┘    └──────────┘   └──────────┘


┌─────────────────────────────────────────────────────────────────┐
│                     OUTGOING MESSAGE FLOW                        │
│                     (Your existing setup)                        │
└─────────────────────────────────────────────────────────────────┘

   Your Backend (Contact form)
          │
          │ POST https://graph.facebook.com/v21.0/{phone_id}/messages
          │ Authorization: Bearer {token}
          │
          ▼
   ┌──────────────────┐
   │  WhatsApp Cloud  │
   │       API        │
   └──────┬───────────┘
          │
          ▼
   ┌──────────────┐
   │   Customer   │ Receives message
   │  📱 Mobile   │
   └──────────────┘
          │
          │ Status updates sent back to your webhook:
          │ • sent
          │ • delivered
          │ • read
          ▼
   Saved in: whatsapp_whatsappmessagestatus
```

## API Endpoints

```
POST   /api/whatsapp/webhook/        ← Facebook posts messages here
GET    /api/whatsapp/webhook/        ← Webhook verification (one-time)
GET    /api/whatsapp/messages/       ← View all messages
GET    /api/whatsapp/conversations/  ← View conversations
POST   /api/whatsapp/mark-read/      ← Mark messages as read
```

## Where to View Messages

### 1. Django Admin (Best for human viewing)
```
https://your-app.fly.dev/admin/whatsapp/whatsappmessage/

Features:
✓ Search by phone/name
✓ Filter by date/type
✓ View full message details
✓ See media files
✓ Read/edit notes
```

### 2. REST API (Best for programmatic access)
```javascript
// Fetch messages
const messages = await fetch('/api/whatsapp/messages/')
  .then(r => r.json());

// Filter by phone
const customerMessages = await fetch(
  '/api/whatsapp/messages/?phone=919876543210'
).then(r => r.json());
```

### 3. Database Query (Best for analytics)
```sql
SELECT 
  from_number,
  COUNT(*) as msg_count,
  MAX(timestamp) as last_message
FROM whatsapp_whatsappmessage
GROUP BY from_number
ORDER BY last_message DESC;
```

## Call Handling

```
❌ WABA API does NOT support calls

Customer tries to call
          │
          ▼
   ┌──────────────────┐
   │  WhatsApp shows: │
   │  "This business  │
   │  account can't   │
   │  receive calls"  │
   └──────────────────┘

SOLUTIONS:

1. Display alternative phone number in business profile
2. Send auto-reply with call instructions
3. Use separate number for calls
4. Add click-to-call button on website
```

## Message Types Handled

```
┌──────────────┬─────────────────────────────────────┐
│ Type         │ What's Stored                       │
├──────────────┼─────────────────────────────────────┤
│ text         │ text_body                           │
│ image        │ media_id, media_url, caption        │
│ video        │ media_id, media_url                 │
│ audio        │ media_id                            │
│ document     │ media_id, media_url                 │
│ location     │ latitude, longitude, name, address  │
│ interactive  │ text_body (button/list selection)   │
└──────────────┴─────────────────────────────────────┘
```

## Security Flow

```
Facebook sends webhook request
          │
          │ Includes header: X-Hub-Signature-256
          ▼
   ┌──────────────────────────────────────┐
   │  Your backend verifies signature:    │
   │                                      │
   │  Expected = HMAC-SHA256(             │
   │    key: WHATSAPP_APP_SECRET,         │
   │    message: request.body             │
   │  )                                   │
   │                                      │
   │  if signature == expected:           │
   │    ✅ Process request                │
   │  else:                               │
   │    ❌ Reject (403 Forbidden)         │
   └──────────────────────────────────────┘
```

## Development vs Production

```
┌──────────────────┬────────────────────────────────────┐
│  Development     │  Production                        │
├──────────────────┼────────────────────────────────────┤
│  localhost:8000  │  your-app.fly.dev                  │
│  + ngrok tunnel  │  Direct HTTPS                      │
│                  │                                    │
│  Webhook URL:    │  Webhook URL:                      │
│  https://        │  https://your-app.fly.dev/         │
│  abc123.ngrok.io │  api/whatsapp/webhook/             │
│  /api/whatsapp/  │                                    │
│  webhook/        │                                    │
└──────────────────┴────────────────────────────────────┘
```
