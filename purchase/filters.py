import django_filters
from .models import PurchaseOrder

class PurchaseOrderFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(choices=PurchaseOrder.STATUS_CHOICES)
    order_date = django_filters.DateFromToRangeFilter()
    supplier = django_filters.CharFilter(field_name="supplier__name", lookup_expr='icontains')

    class Meta:
        model = PurchaseOrder
        fields = ['status', 'order_date', 'supplier']
