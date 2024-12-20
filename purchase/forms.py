from django import forms
from django.forms import inlineformset_factory
from .models import PurchaseOrder, PurchaseOrderLine

class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['po_number', 'supplier', 'order_date', 'status']

class PurchaseOrderLineForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderLine
        fields = ['product', 'quantity', 'unit_price']

PurchaseOrderLineFormSet = inlineformset_factory(
    PurchaseOrder, PurchaseOrderLine, 
    form=PurchaseOrderLineForm,
    extra=1,  
    can_delete=True
)
