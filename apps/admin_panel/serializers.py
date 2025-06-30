# admin_panel/serializers.py
from rest_framework import serializers
from apps.store.models import Product

class ProductStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['sku', 'name', 'stock']