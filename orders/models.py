from django.db import models
from store.models import Product


class Order(models.Model):
    PENDING, CONFIRMED, SHIPPED, DELIVERED, DONE, CANCELLED = (
        "pending", "confirmed", "shipped", "delivered", "done", "cancelled")
    STATUS = [(PENDING, "Pending"), (CONFIRMED, "Confirmed"), (SHIPPED, "Shipped"),
              (DELIVERED, "Delivered"), (DONE, "Done"), (CANCELLED, "Cancelled")]

    full_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=30)
    wilaya = models.CharField("Wilaya / city", max_length=80)
    address = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=STATUS, default=PENDING)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.pk}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=140)  # snapshot, survives product deletion
    price = models.DecimalField(max_digits=10, decimal_places=2)
    size = models.CharField(max_length=20, blank=True)
    color = models.CharField(max_length=40, blank=True)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def subtotal(self):
        return self.price * self.quantity
