from django.db import models
from django.conf import settings
from decimal import Decimal

class Order(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_PAID = 'paid'
    STATUS_FAILED = 'failed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pendiente'),
        (STATUS_PAID, 'Pagado'),
        (STATUS_FAILED, 'Fallido'),
        (STATUS_CANCELLED, 'Cancelado'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    shipping_address = models.CharField(max_length=255, default="")
    shipping_city = models.CharField(max_length=100, default="")
    shipping_region = models.CharField(max_length=100, default="")
    shipping_zip = models.CharField(max_length=20, default="")
    notes = models.TextField(blank=True, null=True)

    # ✅ Campo único para evitar que una orden se duplique al refrescar
    payment_token = models.CharField(max_length=100, unique=True, null=True, blank=True)

    def __str__(self):
        return f"Pedido #{self.id} - {self.user.username} - {self.status}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    sku = models.CharField(max_length=100)
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=2)  # Precio unitario

    def __str__(self):
        return f"{self.quantity} x {self.product_name} (SKU: {self.sku})"

    @property
    def subtotal(self):
        if self.price is None or self.quantity is None:
            return Decimal('0.00')
        return self.price * self.quantity