from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import BillSerializer
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
import logging
import requests
import os
from decimal import Decimal
import json

logger = logging.getLogger(__name__)

@method_decorator(ratelimit(key='ip', rate='20/m', block=True), name='dispatch')
class BillCreateView(APIView):
    def post(self, request):
        ip = request.META.get('REMOTE_ADDR')
        logger.info(f"POST /api/bills/create/ from {ip} — Data: {request.data}")

        serializer = BillSerializer(data=request.data)
        if serializer.is_valid():
            # Save bill to database
            bill = serializer.save()
            
            logger.info(f"✅ Bill {bill.slip_no} saved to database")
            
            # Send WhatsApp notification to customer
            whatsapp_sent = self.send_whatsapp_notification(bill)
            
            if whatsapp_sent:
                logger.info(f"✅ ✅ ✅ WhatsApp sent successfully to {bill.phone} for slip {bill.slip_no}")
            else:
                logger.warning(f"⚠️ ⚠️ ⚠️ WhatsApp FAILED for {bill.phone}, but bill {bill.slip_no} was created")
            
            response_data = {
                'message': 'Bill created successfully!',
                'whatsapp_sent': whatsapp_sent,
                'slip_no': bill.slip_no,
                'customer_phone': bill.phone
            }
            
            logger.info(f"📤 Sending response: {response_data}")
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            # Log detailed validation errors for debugging
            logger.error(f"Validation errors: {serializer.errors}")
            return Response({
                'error': 'Validation failed',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def send_whatsapp_notification(self, bill):
        """
        Send WhatsApp notification to customer when bill is created using template
        """
        try:
            logger.info(f"🚀 Starting WhatsApp notification for bill {bill.slip_no}")
            
            # Get WhatsApp credentials
            whatsapp_token = os.getenv('WHATSAPP_ACCESS_TOKEN')
            phone_number_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
            template_name = os.getenv('WHATSAPP_TEMPLATE_NAME', 'order_slip')  # Using order_slip template with button
            
            logger.info(f"📋 Token present: {bool(whatsapp_token)}, Phone ID: {phone_number_id}, Template: {template_name}")
            
            if not all([whatsapp_token, phone_number_id]):
                logger.error("❌ WhatsApp credentials not configured in .env")
                return False
            
            # Calculate total amount
            total_amount = sum(
                item.quantity * item.price_per_unit 
                for item in bill.items.all()
            )
            logger.info(f"💰 Total amount calculated: ₹{total_amount}")
            
            # Format items list for template
            items_text = self._format_items_list(bill)
            logger.info(f"✉️ Items formatted")
            
            # Customer's phone number (from bill)
            customer_phone = bill.phone
            logger.info(f"📱 Original phone from bill: {customer_phone}")
            
            # Ensure phone is in international format (91 + 10 digits)
            if not customer_phone.startswith('91'):
                customer_phone = f'91{customer_phone}'
            
            # Remove any spaces, dashes, or special characters
            customer_phone = customer_phone.replace('+', '').replace('-', '').replace(' ', '')
            logger.info(f"📱 Formatted phone for WhatsApp: {customer_phone}")
            
            # WhatsApp API endpoint
            url = f"https://graph.facebook.com/v22.0/{phone_number_id}/messages"
            logger.info(f"🌐 API URL: {url}")
            
            headers = {
                "Authorization": f"Bearer {whatsapp_token}",
                "Content-Type": "application/json"
            }
            
            # Build template payload with NAMED parameters
            payload = {
                "messaging_product": "whatsapp",
                "to": customer_phone,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {"code": "en"},
                    "components": [
                        {
                            "type": "header",
                            "parameters": [
                                {
                                    "type": "text",
                                    "parameter_name": "order_id",
                                    "text": str(bill.slip_no)
                                }
                            ]
                        },
                        {
                            "type": "body",
                            "parameters": [
                                {
                                    "type": "text",
                                    "parameter_name": "order_date",
                                    "text": bill.date.strftime('%d-%b-%Y')
                                },
                                {
                                    "type": "text",
                                    "parameter_name": "due_date",
                                    "text": bill.due_date.strftime('%d-%b-%Y')
                                },
                                {
                                    "type": "text",
                                    "parameter_name": "address",
                                    "text": str(bill.address) if bill.address else "N/A"
                                },
                                {
                                    "type": "text",
                                    "parameter_name": "order_items",
                                    "text": items_text if items_text else "No items"
                                },
                                {
                                    "type": "text",
                                    "parameter_name": "amount",
                                    "text": str(total_amount) if total_amount else "0"
                                }
                            ]
                        }
                    ]
                }
            }
            logger.info("📦 WhatsApp Payload: %s", json.dumps(payload, indent=2))
            logger.info(f"📦 Payload ready. Sending template to: {customer_phone}")
            
            # Send request
            logger.info("⏳ Calling WhatsApp API...")
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            logger.info(f"📊 WhatsApp API Response Status: {response.status_code}")
            logger.info(f"📊 WhatsApp API Response Body: {response.text}")
            
            if response.status_code == 200:
                logger.info(f"✅ WhatsApp sent successfully: {response.json()}")
                return True
            else:
                logger.error(f"❌ WhatsApp API error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"💥 Exception sending WhatsApp: {str(e)}")
            import traceback
            logger.error(f"Stack trace: {traceback.format_exc()}")
            return False
    
    def _format_items_list(self, bill):
        """
        Format items list for WhatsApp template parameter
        """
        items_text = ""
        for index, item in enumerate(bill.items.all(), start=1):
            items_text += f"{index}. {item.item_name} ({item.service}) — {item.quantity} × ₹{item.price_per_unit}\n"
        
        return items_text.strip()