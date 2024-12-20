# purchase/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .apis import SupplierViewSet, ProductViewSet, PurchaseOrderViewSet

router = DefaultRouter()
router.register(r'suppliers', SupplierViewSet)  # This registers /suppliers/ endpoint
router.register(r'products', ProductViewSet)
router.register(r'purchaseorders', PurchaseOrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
