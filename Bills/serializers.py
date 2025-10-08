from rest_framework import serializers
from .models import slip, items

class BillItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = items
        fields = ['item_name', 'service', 'quantity', 'price_per_unit']

class BillSerializer(serializers.ModelSerializer):
    items = BillItemSerializer(many=True)  # Nested serializer

    class Meta:
        model = slip
        fields = ['slip_no', 'date', 'due_date', 'address', 'phone', 'items', 'amount']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        bill_slip = slip.objects.create(**validated_data)
        for item in items_data:
            items.objects.create(slip=bill_slip, **item)
        return bill_slip
