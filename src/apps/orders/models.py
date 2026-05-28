from django.db import models


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(
        'accounts.User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='orders'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True
    )
    total = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.JSONField()
    shipping_method = models.CharField(max_length=50, blank=True)
    shipping_cost = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    has_unread_update = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self):
        return f"Order #{self.id} - {self.status}"

    def save(self, *args, **kwargs):
        # Check if this is an existing order and status has changed
        if self.pk and self.user:
            orig = Order.objects.get(pk=self.pk)
            if orig.status != self.status:
                self.has_unread_update = True
                self.user.has_unread_orders = True
                self.user.save(update_fields=['has_unread_orders'])
        elif not self.pk and self.user:
            # New order
            pass
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='line_items'
    )
    product = models.ForeignKey(
        'store.Product',
        on_delete=models.PROTECT,
        related_name='order_lines'
    )
    variant = models.ForeignKey(
        'store.Variant',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='order_lines'
    )
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.product.name} (Order #{self.order_id})"
