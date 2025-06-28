# TapTogetherBackend/bills_api/serializers.py

from rest_framework import serializers
from .models import Bill, BillItem

class BillItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillItem
        fields = ['id', 'description', 'price']

class BillSerializer(serializers.ModelSerializer):
    items = BillItemSerializer(many=True, read_only=True) # Nested serializer to include bill items when a bill is retrieved

    class Meta:
        model = Bill
        fields = ['id', 'uploaded_image', 'upload_date', 'total_amount', 'gemini_raw_response', 'is_processed', 'items']
        read_only_fields = ['upload_date', 'total_amount', 'gemini_raw_response', 'is_processed', 'items'] # These fields are set by the backend, not by the client upload