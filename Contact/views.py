from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ContactSerializer
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
import logging
import requests
import os

logger = logging.getLogger(__name__)


@method_decorator(ratelimit(key='ip', rate='10/h', block=True), name='dispatch')
class ContactSubmitView(APIView):
    """
    API endpoint to handle contact form submissions and forward via WhatsApp
    """
    
    def post(self, request):
        ip = request.META.get('REMOTE_ADDR')
        logger.info(f"POST /api/contact/ from {ip} — Data: {request.data}")

        # Validate incoming data
        serializer = ContactSerializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Validation errors: {serializer.errors}")
            return Response({
                'code': 400,
                'error': 'Validation failed',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # Extract validated data
        contact_data = serializer.validated_data
        
        # Send WhatsApp message
        whatsapp_success = self.send_whatsapp_message(contact_data)
        
        if whatsapp_success:
            logger.info(f"Contact form submitted successfully from {ip}")
            return Response({
                'code': 200,
                'message': 'Contact form submitted successfully!'
            }, status=status.HTTP_200_OK)
        else:
            logger.error(f"Failed to send WhatsApp message for submission from {ip}")
            return Response({
                'code': 500,
                'error': 'Failed to send message. Please try again or contact us directly.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def send_whatsapp_message(self, contact_data):
        """
        Send contact form data via WhatsApp Business API using template
        """
        try:
            # Get WhatsApp credentials from environment
            whatsapp_token = os.getenv('WHATSAPP_ACCESS_TOKEN')
            phone_number_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
            recipient_number = os.getenv('WHATSAPP_RECIPIENT_NUMBER')  # Your receiving number
            template_name = 'contact_query'
            
            if not all([whatsapp_token, phone_number_id, recipient_number]):
                logger.error("WhatsApp credentials not configured in environment variables")
                return False
            
            # WhatsApp Cloud API endpoint
            url = f"https://graph.facebook.com/v21.0/{phone_number_id}/messages"
            
            headers = {
                "Authorization": f"Bearer {whatsapp_token}",
                "Content-Type": "application/json"
            }
            
            # Ensure recipient number is in international format (without +)
            # e.g., 919876543210 for India
            recipient = recipient_number.replace('+', '').replace('-', '').replace(' ', '')
            
            # Construct template message payload (body only, 4 parameters)
            payload = {
                "messaging_product": "whatsapp",
                "to": recipient,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {
                        "code": "en"
                    },
                    "components": [
                        {
                            "type": "header",
                            "parameters": [
                                {
                                    "type": "text",
                                    "parameter_name": "subject",
                                    "text": contact_data['subject']
                                }
                            ]
                        },
                        {
                            "type": "body",
                            "parameters": [
                                {
                                    "type": "text",
                                    "parameter_name": "name",
                                    "text": contact_data['name']
                                },
                                {
                                    "type": "text",
                                    "parameter_name": "phone",
                                    "text": contact_data['phone']
                                },
                                {
                                    "type": "text",
                                    "parameter_name": "message",
                                    "text": contact_data['message']
                                }
                            ]
                        }
                    ]
                }
            }
            # Send request
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"WhatsApp message sent successfully: {response.json()}")
                return True
            else:
                logger.error(f"WhatsApp API error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Exception while sending WhatsApp message: {str(e)}")
            return False
