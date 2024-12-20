from rest_framework import serializers
from .models import Supplier, Product, PurchaseOrder, PurchaseOrderLine
from django.core.exceptions import ValidationError

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
        fields = ['po_number', 'supplier', 'order_date', 'status', 'total_amount', 'created_at', 'updated_at', 'lines']
    
    def validate_supplier(self, value):
        if not value.active:
            raise ValidationError("The supplier is not active.")
        return value
    
    def validate(self, data):
        total_amount = 0
        for line in data.get('lines', []):
            total_amount += line['quantity'] * line['unit_price']
        
        data['total_amount'] = total_amount
        return data

    def create(self, validated_data):
        lines_data = validated_data.pop('lines')
        purchase_order = PurchaseOrder.objects.create(**validated_data)
        
        for line_data in lines_data:
            product = line_data['product']
            quantity = line_data['quantity']
            
            product.current_stock -= quantity
            product.save()
            
            PurchaseOrderLine.objects.create(purchase_order=purchase_order, **line_data)
        
        return purchase_order
