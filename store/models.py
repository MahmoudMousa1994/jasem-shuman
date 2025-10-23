from django.db import models
from django.contrib.auth.models import User
from gallery.models import Artwork, TimestampedModel


class Order(TimestampedModel):
    """Customer orders"""
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    customer = models.ForeignKey(User, on_delete=models.PROTECT)
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    
    # Pricing breakdown
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Notes
    customer_notes = models.TextField(blank=True, help_text="Special instructions from customer")
    admin_notes = models.TextField(blank=True, help_text="Internal notes")
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order #{self.id} - {self.customer.username} - ${self.total_amount}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate total
        if self.subtotal is not None and self.shipping_cost is not None:
            self.total_amount = self.subtotal + self.shipping_cost
        super().save(*args, **kwargs)


class OrderItem(TimestampedModel):
    """Individual items within an order"""
    ITEM_TYPE_CHOICES = [
        ('original', 'Original Artwork'),
        ('print', 'Print Copy'),
        ('photo_set', 'Signed Photo Set'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    artwork = models.ForeignKey(Artwork, on_delete=models.PROTECT)
    item_type = models.CharField(max_length=15, choices=ITEM_TYPE_CHOICES)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.artwork.title} ({self.get_item_type_display()}) - {self.quantity}x"
    
    def save(self, *args, **kwargs):
        # Auto-calculate total price
        if self.unit_price and self.quantity:
            self.total_price = self.unit_price * self.quantity
        
        # Set unit price based on item type if not set
        if not self.unit_price:
            if self.item_type == 'original':
                self.unit_price = self.artwork.original_price
            else:
                self.unit_price = self.artwork.second_option_price
            self.total_price = self.unit_price * self.quantity
        
        super().save(*args, **kwargs)
        
        # Update artwork inventory
        if self.item_type != 'original':
            self.artwork.sold_second_option_copies += self.quantity
            self.artwork.save()
        else:
            self.artwork.original_available = False
            self.artwork.save()


class ShippingAddress(TimestampedModel):
    """Shipping addresses for orders"""
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='shipping_address')
    
    # Contact info
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    
    # Address
    address_line_1 = models.CharField(max_length=200, help_text="Street address")
    address_line_2 = models.CharField(max_length=200, blank=True, help_text="Apartment, suite, etc.")
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default="United States")
    
    # Delivery preferences
    delivery_instructions = models.TextField(blank=True, help_text="Special delivery instructions")
    
    def __str__(self):
        return f"Shipping to {self.full_name} - Order #{self.order.id}"
    
    @property
    def full_address(self):
        """Get formatted full address"""
        address = f"{self.address_line_1}"
        if self.address_line_2:
            address += f", {self.address_line_2}"
        address += f", {self.city}, {self.state} {self.postal_code}, {self.country}"
        return address


class PaymentInfo(TimestampedModel):
    """Payment information for orders"""
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash_on_delivery', 'Cash on Delivery'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment_info')
    
    # Payment method
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    
    # Card info (only last 4 digits stored for security)
    cardholder_name = models.CharField(max_length=200, blank=True)
    card_last_four = models.CharField(max_length=4, blank=True, help_text="Last 4 digits only")
    
    # Bank transfer details
    bank_details = models.TextField(blank=True, help_text="Bank transfer information")
    
    # Payment status
    is_paid = models.BooleanField(default=False)
    payment_date = models.DateTimeField(null=True, blank=True)
    payment_notes = models.TextField(blank=True)
    
    # Transaction reference
    transaction_reference = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"Payment for Order #{self.order.id} - {self.get_payment_method_display()}"
    
    def mark_as_paid(self):
        """Mark payment as completed"""
        from django.utils import timezone
        self.is_paid = True
        self.payment_date = timezone.now()
        self.save()
        
        # Update order status
        self.order.order_status = 'confirmed'
        self.order.save()


class Cart(TimestampedModel):
    """Shopping cart for session-based or user-based shopping"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=32, null=True, blank=True)
    
    def __str__(self):
        if self.user:
            return f"Cart for {self.user.username}"
        return f"Anonymous cart ({self.session_key})"
    
    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())
    
    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())


class CartItem(TimestampedModel):
    """Items in shopping cart"""
    ITEM_TYPE_CHOICES = [
        ('original', 'Original Artwork'),
        ('print', 'Print Copy'),
        ('photo_set', 'Signed Photo Set'),
    ]
    
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE)
    item_type = models.CharField(max_length=15, choices=ITEM_TYPE_CHOICES)
    quantity = models.PositiveIntegerField(default=1)
    
    class Meta:
        unique_together = ['cart', 'artwork', 'item_type']
    
    def __str__(self):
        return f"{self.artwork.title} ({self.get_item_type_display()}) - {self.quantity}x"
    
    @property
    def unit_price(self):
        if self.item_type == 'original':
            return self.artwork.original_price
        return self.artwork.second_option_price
    
    @property
    def total_price(self):
        return self.unit_price * self.quantity
