from rest_framework import serializers


class ContactSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200, required=True)
    phone = serializers.CharField(max_length=20, required=True)
    subject = serializers.CharField(max_length=300, required=True)
    message = serializers.CharField(required=True)

    def validate_phone(self, value):
        """Validate phone number format (10 digits)"""
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError("Phone number must be exactly 10 digits.")
        return value
