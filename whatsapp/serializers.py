from rest_framework import serializers
from .models import WhatsAppMessage, WhatsAppMessageStatus, WhatsAppConversation


class WhatsAppMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhatsAppMessage
        fields = '__all__'


class WhatsAppMessageStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhatsAppMessageStatus
        fields = '__all__'


class WhatsAppConversationSerializer(serializers.ModelSerializer):
    latest_messages = serializers.SerializerMethodField()
    
    class Meta:
        model = WhatsAppConversation
        fields = '__all__'
    
    def get_latest_messages(self, obj):
        messages = WhatsAppMessage.objects.filter(
            from_number=obj.phone_number
        ).order_by('-timestamp')[:10]
        return WhatsAppMessageSerializer(messages, many=True).data
