from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import (SupplierSerializer, ProductSerializer, 
                         PurchaseOrderSerializer)
from .models import Supplier, Product, PurchaseOrder
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .filters import PurchaseOrderFilter
from rest_framework import status


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ['name', 'email']
    ordering_fields = ['name', 'code']
    ordering = ['name']
    
    def destroy(self, request, *args, **kwargs):
        supplier = self.get_object()
        
        if PurchaseOrder.objects.filter(supplier=supplier, status__in=['SUBMITTED', 'APPROVED']).exists():
            return Response({"error": "Cannot delete supplier with active purchase orders."}, status=status.HTTP_400_BAD_REQUEST)
        
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['get'])
    def purchase_history(self, request, pk=None):
        supplier = self.get_object()
        purchase_orders = PurchaseOrder.objects.filter(supplier=supplier)
        serializer = PurchaseOrderSerializer(purchase_orders, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def update_stock(self, request, pk=None):
        product = self.get_object()
        new_stock = request.data.get('new_stock', None)
        
        if new_stock is None:
            return Response({"error": "New stock value is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        product.current_stock = new_stock
        product.save()
        return Response({"message": "Stock updated successfully."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def low_stock_alerts(self, request):
        low_stock_products = Product.objects.filter(current_stock__lt=F('minimum_stock'))
        serializer = ProductSerializer(low_stock_products, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def price_history(self, request, pk=None):
        product = self.get_object()
        price_history = ProductPriceHistory.objects.filter(product=product).order_by('-date')
        serializer = ProductPriceHistorySerializer(price_history, many=True)
        return Response(serializer.data)    


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = PurchaseOrderFilter
    ordering_fields = ['order_date', 'total_amount', 'status']
    ordering = ['order_date']

    @action(detail=False, methods=['post'])
    def create_purchase_order(self, request):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        purchase_order = self.get_object()
        new_status = request.data.get('status', None)
        
        if not new_status:
            return Response({"error": "No status provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        valid_transitions = {
            'DRAFT': ['SUBMITTED'],
            'SUBMITTED': ['APPROVED'],
            'APPROVED': ['COMPLETED'],
        }
        
        current_status = purchase_order.status
        
        if new_status not in valid_transitions.get(current_status, []):
            return Response({
                "error": f"Invalid status transition from {current_status} to {new_status}"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        purchase_order.status = new_status
        purchase_order.save()

        if new_status == 'COMPLETED':
            for line in purchase_order.lines.all():
                product = line.product
                product.current_stock += line.quantity
                product.save()

                send_mail(
                    'Purchase Order Status Updated',
                    f'Your purchase order {purchase_order.po_number} has been updated to {new_status}.',
                    'from@example.com',
                    [purchase_order.supplier.email],
                    fail_silently=False,
                )

        return Response(self.get_serializer(purchase_order).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['put'])
    def update_purchase_order(self, request, pk=None):
        purchase_order = self.get_object()

        if purchase_order.status == 'COMPLETED':
            return Response({"error": "Completed orders cannot be modified"}, status=status.HTTP_400_BAD_REQUEST)
        
        new_status = request.data.get('status', None)
        if new_status:
            valid_transitions = {
                'DRAFT': ['SUBMITTED'],
                'SUBMITTED': ['APPROVED'],
                'APPROVED': ['COMPLETED'],
            }
            
            current_status = purchase_order.status
            if new_status not in valid_transitions.get(current_status, []):
                return Response({
                    "error": f"Invalid status transition from {current_status} to {new_status}"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            purchase_order.status = new_status
        
        serializer = self.get_serializer(purchase_order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)