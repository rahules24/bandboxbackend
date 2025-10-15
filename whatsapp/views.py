from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import transaction
from datetime import datetime
import logging
import os
import hmac
import hashlib
import requests

from .models import WhatsAppMessage, WhatsAppMessageStatus, WhatsAppConversation
from .serializers import WhatsAppMessageSerializer, WhatsAppConversationSerializer

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class WhatsAppWebhookView(APIView):
    """
    Main webhook endpoint for receiving WhatsApp messages and status updates
    
    Facebook will send:
    - GET request for verification (one-time setup)
    - POST requests for incoming messages and status updates
    """
    
    def get(self, request):
        """
        Webhook verification - Facebook sends this during setup
        
        You'll receive:
        - hub.mode: 'subscribe'
        - hub.verify_token: The token you set in Meta Developer Console
        - hub.challenge: A random string to echo back
        """
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')
        
        # Get your verify token from environment
        verify_token = os.getenv('WHATSAPP_WEBHOOK_VERIFY_TOKEN', 'your_verify_token_here')
        
        if mode == 'subscribe' and token == verify_token:
            logger.info('Webhook verified successfully!')
            return Response(int(challenge), status=status.HTTP_200_OK)
        else:
            logger.error(f'Webhook verification failed. Mode: {mode}, Token match: {token == verify_token}')
            return Response({'error': 'Verification failed'}, status=status.HTTP_403_FORBIDDEN)
    
    def post(self, request):
        """
        Handle incoming webhook events (messages, status updates)
        """
        try:
            # Verify webhook signature (optional but recommended for security)
            if not self._verify_signature(request):
                logger.warning('Invalid webhook signature')
                return Response({'error': 'Invalid signature'}, status=status.HTTP_403_FORBIDDEN)
            
            data = request.data
            logger.info(f'Received webhook: {data}')
            
            # WhatsApp sends data in this structure
            if data.get('object') == 'whatsapp_business_account':
                for entry in data.get('entry', []):
                    for change in entry.get('changes', []):
                        value = change.get('value', {})
                        
                        # Handle incoming messages
                        if 'messages' in value:
                            self._handle_messages(value)
                        
                        # Handle status updates (sent, delivered, read, failed)
                        if 'statuses' in value:
                            self._handle_statuses(value)
            
            # Always return 200 OK to acknowledge receipt
            return Response({'status': 'success'}, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f'Error processing webhook: {str(e)}', exc_info=True)
            # Still return 200 to prevent Facebook from retrying
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_200_OK)
    
    def _verify_signature(self, request):
        """
        Verify webhook signature from Facebook
        """
        try:
            signature = request.META.get('HTTP_X_HUB_SIGNATURE_256', '')
            if not signature:
                return True  # Skip if signature not provided (for testing)
            
            app_secret = os.getenv('WHATSAPP_APP_SECRET', '')
            if not app_secret:
                return True  # Skip if app secret not configured
            
            # Calculate expected signature
            expected_signature = 'sha256=' + hmac.new(
                app_secret.encode('utf-8'),
                request.body,
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
        except Exception as e:
            logger.error(f'Signature verification error: {str(e)}')
            return False
    
    @transaction.atomic
    def _handle_messages(self, value):
        """
        Process incoming messages
        """
        messages = value.get('messages', [])
        metadata = value.get('metadata', {})
        contacts = value.get('contacts', [])
        
        for message in messages:
            try:
                # Extract message data
                message_id = message.get('id')
                from_number = message.get('from')
                timestamp = datetime.fromtimestamp(int(message.get('timestamp')))
                message_type = message.get('type')
                
                # Check if message already exists
                if WhatsAppMessage.objects.filter(message_id=message_id).exists():
                    logger.info(f'Message {message_id} already processed')
                    continue
                
                # Get contact name if available
                contact_name = None
                for contact in contacts:
                    if contact.get('wa_id') == from_number:
                        contact_name = contact.get('profile', {}).get('name')
                        break
                
                # Extract message content based on type
                text_body = None
                media_id = None
                media_mime_type = None
                media_caption = None
                latitude = None
                longitude = None
                location_name = None
                location_address = None
                context_message_id = None
                
                if message_type == 'text':
                    text_body = message.get('text', {}).get('body')
                
                elif message_type in ['image', 'video', 'audio', 'document']:
                    media_data = message.get(message_type, {})
                    media_id = media_data.get('id')
                    media_mime_type = media_data.get('mime_type')
                    media_caption = media_data.get('caption', '')
                
                elif message_type == 'location':
                    location = message.get('location', {})
                    latitude = location.get('latitude')
                    longitude = location.get('longitude')
                    location_name = location.get('name')
                    location_address = location.get('address')
                
                elif message_type == 'interactive':
                    interactive = message.get('interactive', {})
                    if interactive.get('type') == 'button_reply':
                        text_body = interactive.get('button_reply', {}).get('title')
                    elif interactive.get('type') == 'list_reply':
                        text_body = interactive.get('list_reply', {}).get('title')
                
                # Check for context (reply to message)
                if 'context' in message:
                    context_message_id = message.get('context', {}).get('id')
                
                # Save message to database
                whatsapp_message = WhatsAppMessage.objects.create(
                    message_id=message_id,
                    wamid=f"wamid.{message_id}",
                    from_number=from_number,
                    from_name=contact_name,
                    message_type=message_type,
                    text_body=text_body,
                    media_id=media_id,
                    media_mime_type=media_mime_type,
                    media_caption=media_caption,
                    latitude=latitude,
                    longitude=longitude,
                    location_name=location_name,
                    location_address=location_address,
                    timestamp=timestamp,
                    context_message_id=context_message_id,
                    raw_payload=message
                )
                
                # Update or create conversation
                conversation, created = WhatsAppConversation.objects.get_or_create(
                    phone_number=from_number,
                    defaults={'contact_name': contact_name}
                )
                conversation.last_message_at = timestamp
                conversation.message_count += 1
                conversation.unread_count += 1
                if contact_name and not conversation.contact_name:
                    conversation.contact_name = contact_name
                conversation.save()
                
                logger.info(f'Saved message {message_id} from {from_number}')
                
                # Download media if present
                if media_id:
                    self._download_media(media_id, whatsapp_message)
                
                # You can add auto-reply logic here
                # self._send_auto_reply(from_number, message_type)
                
            except Exception as e:
                logger.error(f'Error processing message: {str(e)}', exc_info=True)
    
    def _handle_statuses(self, value):
        """
        Process message status updates (sent, delivered, read, failed)
        """
        statuses = value.get('statuses', [])
        
        for status_update in statuses:
            try:
                message_id = status_update.get('id')
                recipient_id = status_update.get('recipient_id')
                status_type = status_update.get('status')
                timestamp = datetime.fromtimestamp(int(status_update.get('timestamp')))
                
                # Extract error info if status is failed
                error_code = None
                error_message = None
                if status_type == 'failed':
                    errors = status_update.get('errors', [])
                    if errors:
                        error_code = errors[0].get('code')
                        error_message = errors[0].get('title')
                
                # Save status update
                WhatsAppMessageStatus.objects.create(
                    message_id=message_id,
                    recipient_number=recipient_id,
                    status=status_type,
                    timestamp=timestamp,
                    error_code=error_code,
                    error_message=error_message,
                    raw_payload=status_update
                )
                
                logger.info(f'Status update: {message_id} -> {status_type}')
                
            except Exception as e:
                logger.error(f'Error processing status: {str(e)}', exc_info=True)
    
    def _download_media(self, media_id, message_obj):
        """
        Download media file from WhatsApp
        """
        try:
            access_token = os.getenv('WHATSAPP_ACCESS_TOKEN')
            
            # Get media URL
            url = f'https://graph.facebook.com/v21.0/{media_id}'
            headers = {'Authorization': f'Bearer {access_token}'}
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                media_data = response.json()
                media_url = media_data.get('url')
                
                # Download the actual file
                media_response = requests.get(media_url, headers=headers)
                if media_response.status_code == 200:
                    # Save to media folder or cloud storage
                    # For now, just save the URL
                    message_obj.media_url = media_url
                    message_obj.save()
                    logger.info(f'Downloaded media {media_id}')
            
        except Exception as e:
            logger.error(f'Error downloading media: {str(e)}')
    
    def _send_auto_reply(self, to_number, message_type):
        """
        Optional: Send automatic reply
        """
        # You can implement auto-reply logic here
        pass


class MessagesListView(APIView):
    """
    API to view all received messages
    """
    def get(self, request):
        """
        Get all messages with optional filters
        
        Query params:
        - phone: Filter by phone number
        - type: Filter by message type
        - limit: Number of messages to return
        """
        phone = request.GET.get('phone')
        msg_type = request.GET.get('type')
        limit = int(request.GET.get('limit', 100))
        
        messages = WhatsAppMessage.objects.all()
        
        if phone:
            messages = messages.filter(from_number=phone)
        if msg_type:
            messages = messages.filter(message_type=msg_type)
        
        messages = messages[:limit]
        serializer = WhatsAppMessageSerializer(messages, many=True)
        
        return Response({
            'count': messages.count(),
            'messages': serializer.data
        })


class ConversationsListView(APIView):
    """
    API to view all conversations grouped by phone number
    """
    def get(self, request):
        conversations = WhatsAppConversation.objects.all()[:50]
        serializer = WhatsAppConversationSerializer(conversations, many=True)
        
        return Response({
            'count': conversations.count(),
            'conversations': serializer.data
        })


class MarkAsReadView(APIView):
    """
    Mark messages from a conversation as read
    """
    def post(self, request):
        phone_number = request.data.get('phone_number')
        
        if not phone_number:
            return Response(
                {'error': 'phone_number is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            conversation = WhatsAppConversation.objects.get(phone_number=phone_number)
            conversation.unread_count = 0
            conversation.save()
            
            WhatsAppMessage.objects.filter(
                from_number=phone_number,
                status='received'
            ).update(status='read')
            
            return Response({'status': 'success'})
        except WhatsAppConversation.DoesNotExist:
            return Response(
                {'error': 'Conversation not found'},
                status=status.HTTP_404_NOT_FOUND
            )
