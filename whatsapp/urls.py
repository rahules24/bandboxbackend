from django.urls import path
from .views import (
    WhatsAppWebhookView,
    MessagesListView,
    ConversationsListView,
    MarkAsReadView,
    WhatsAppMediaProxyView
)

urlpatterns = [
    # Webhook endpoint - this is where Facebook will send messages
    path('webhook/', WhatsAppWebhookView.as_view(), name='whatsapp-webhook'),
    
    # API endpoints to view messages
    path('messages/', MessagesListView.as_view(), name='messages-list'),
    path('conversations/', ConversationsListView.as_view(), name='conversations-list'),
    path('mark-read/', MarkAsReadView.as_view(), name='mark-read'),
    
    # Media proxy - serves WhatsApp media with authentication
    path('media/<str:media_id>/', WhatsAppMediaProxyView.as_view(), name='whatsapp-media'),
]
