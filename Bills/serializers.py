from rest_framework import serializers
from .models import Bill, BillItem

class BillItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillItem
        fields = ['item_name', 'service', 'quantity', 'price_per_unit']

class BillSerializer(serializers.ModelSerializer):
    items = BillItemSerializer(many=True)  # Nested serializer

    class Meta:
        model = Bill
        fields = ['slip_no', 'date', 'due_date', 'address', 'phone', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        bill = Bill.objects.create(**validated_data)
        for item in items_data:
            BillItem.objects.create(bill=bill, **item)
        return bill
