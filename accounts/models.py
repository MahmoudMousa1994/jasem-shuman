from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from gallery.models import TimestampedModel


class UserProfile(TimestampedModel):
    """Extended user profile information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Contact information
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    # Address information (default shipping)
    address_line_1 = models.CharField(max_length=200, blank=True)
    address_line_2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True, default="United States")
    
    # Preferences
    newsletter_subscription = models.BooleanField(default=False)
    email_notifications = models.BooleanField(default=True)
    preferred_currency = models.CharField(max_length=3, default='USD', choices=[
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('GBP', 'British Pound'),
        ('CAD', 'Canadian Dollar'),
    ])
    
    # Profile image
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    
    # Bio for art collectors/enthusiasts
    bio = models.TextField(blank=True, help_text="Tell us about your interest in art")
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    @property
    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username
    
    @property
    def has_complete_address(self):
        """Check if user has complete shipping address"""
        required_fields = [self.address_line_1, self.city, self.state, self.postal_code]
        return all(field.strip() for field in required_fields)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create profile when user is created"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save profile when user is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()


class WishlistItem(TimestampedModel):
    """User's artwork wishlist"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items')
    artwork = models.ForeignKey('gallery.Artwork', on_delete=models.CASCADE)
    item_type = models.CharField(max_length=15, choices=[
        ('original', 'Original Artwork'),
        ('print', 'Print Copy'),
        ('photo_set', 'Signed Photo Set'),
    ], default='original')
    
    class Meta:
        unique_together = ['user', 'artwork', 'item_type']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.artwork.title} ({self.get_item_type_display()})"


class CustomerInquiry(TimestampedModel):
    """Customer inquiries and contact form submissions"""
    INQUIRY_TYPES = [
        ('general', 'General Inquiry'),
        ('commission', 'Commission Request'),
        ('purchase', 'Purchase Question'),
        ('shipping', 'Shipping Question'),
        ('technical', 'Technical Support'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    # Contact information
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    
    # Inquiry details
    inquiry_type = models.CharField(max_length=20, choices=INQUIRY_TYPES, default='general')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    
    # Related artwork (optional)
    related_artwork = models.ForeignKey('gallery.Artwork', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    admin_response = models.TextField(blank=True)
    response_date = models.DateTimeField(null=True, blank=True)
    
    # User reference (if logged in)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Customer Inquiries"
    
    def __str__(self):
        return f"{self.name} - {self.subject} ({self.get_status_display()})"
