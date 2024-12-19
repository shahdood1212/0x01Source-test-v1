from rest_framework import serializers
from .models import Supplier, Product, PurchaseOrder, PurchaseOrderLine

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'code', 'email', 'phone', 'active']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'code', 'unit_price', 'current_stock', 'minimum_stock']

class PurchaseOrderLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrderLine
        fields = ['id', 'product', 'quantity', 'unit_price', 'line_total']

class PurchaseOrderSerializer(serializers.ModelSerializer):
    lines = PurchaseOrderLineSerializer(many=True)
    
    class Meta:
        model = PurchaseOrder
        fields = ['id', 'po_number', 'supplier', 'order_date', 'status', 
                 'total_amount', 'created_at', 'updated_at', 'lines']