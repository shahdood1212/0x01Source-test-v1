from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import F
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

class Supplier(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class Product(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_stock = models.IntegerField(default=0)
    minimum_stock = models.IntegerField(default=0)
    
    price_history = models.ManyToManyField('PriceHistory', related_name='products', blank=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    def increase_stock(self, quantity):
        self.current_stock += quantity
        self.save()

    def decrease_stock(self, quantity):
        if self.current_stock >= quantity:
            self.current_stock -= quantity
            self.save()
        else:
            raise ValueError(f"Not enough stock to decrease. Available: {self.current_stock}, Requested: {quantity}")

    def is_low_stock(self):
        return self.current_stock < self.minimum_stock

    def add_price_history(self, new_price):
        price_entry = PriceHistory.objects.create(product=self, price=new_price)
        self.price_history.add(price_entry)
        self.save()

class PriceHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date_changed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.price} on {self.date_changed}"

class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted'),
        ('APPROVED', 'Approved'),
        ('COMPLETED', 'Completed')
    ]
    
    po_number = models.CharField(max_length=20, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT)
    order_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"PO-{self.po_number}"

    def validate_status_transition(self, new_status):
        valid_transitions = {
            'DRAFT': ['SUBMITTED'],
            'SUBMITTED': ['APPROVED'],
            'APPROVED': ['COMPLETED'],
        }
        current_status = self.status
        if new_status not in valid_transitions.get(current_status, []):
            raise ValueError(f"Invalid status transition from {current_status} to {new_status}")

    def calculate_total_amount(self):
        total = sum(line.line_total for line in self.lines.all())
        self.total_amount = total
        self.save()

    def is_order_completed(self):
        return self.status == 'COMPLETED'

class PurchaseOrderLine(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, related_name='lines', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    @property
    def line_total(self):
        return self.quantity * self.unit_price
