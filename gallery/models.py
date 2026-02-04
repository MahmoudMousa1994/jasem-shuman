from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class TimestampedModel(models.Model):
    """Abstract base class for models that need timestamps"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class Category(TimestampedModel):
    """Art categories: painting, sculpture, photography, etc."""
    
    name = models.CharField(max_length=50, unique=True, help_text="Category name (e.g., painting, sculpture, photography)")
    display_name = models.CharField(max_length=100, help_text="Display name for the category")
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['display_name']
    
    def __str__(self):
        return self.display_name


class Artwork(TimestampedModel):
    """Main artwork model - supports 4 categories: original paintings, original sculptures, signed prints, signed photo sets"""
    
    # Basic artwork info
    title = models.CharField(max_length=200)
    description = models.TextField()
    artist_statement = models.TextField(help_text="Artist's statement about this piece")
    
    # When Jasem actually created this artwork
    artwork_creation_date = models.DateField(help_text="When Jasem created this artwork")
    
    # Dimensions
    height = models.DecimalField(max_digits=8, decimal_places=2, help_text="Height in cm")
    width = models.DecimalField(max_digits=8, decimal_places=2, help_text="Width in cm")
    depth = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Depth in cm (for sculptures)")
    
    # Media files
    main_image = models.ImageField(upload_to='artworks/')
    artwork_video = models.FileField(upload_to='artworks/videos/', null=True, blank=True, help_text="Video of the artwork")
    
    # Pricing & availability
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price for this item")
    is_available = models.BooleanField(default=True, help_text="Is this item available for purchase?")
    
    # Limited edition inventory (for prints and photo sets only)
    is_limited_edition = models.BooleanField(default=False, help_text="Check if this is a limited edition (prints/photo sets)")
    total_copies = models.PositiveIntegerField(default=0, help_text="Total number of copies available (0 = unlimited)")
    sold_copies = models.PositiveIntegerField(default=0, help_text="Number of copies sold")
    
    # Link to original artwork (for prints and photo sets)
    original_artwork = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, 
                                        related_name='editions',
                                        help_text="Link to the original artwork (for prints/photo sets only)")
    
    # Relations
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    
    # System fields
    is_active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False, help_text="Show on homepage")
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.artwork_creation_date.year})"
    
    def get_absolute_url(self):
        return reverse('gallery:artwork_detail', kwargs={'pk': self.pk})
    
    @property
    def dimensions_display(self):
        """Format dimensions for display"""
        if self.depth:
            return f"{self.height} × {self.width} × {self.depth} cm"
        return f"{self.height} × {self.width} cm"
    
    @property
    def remaining_copies(self):
        """Calculate remaining copies for limited editions"""
        if not self.is_limited_edition or self.total_copies == 0:
            return None
        return self.total_copies - self.sold_copies
    
    @property
    def copies_available(self):
        """Check if copies are still available"""
        if not self.is_limited_edition:
            return self.is_available
        if self.total_copies == 0:  # Unlimited
            return self.is_available
        return self.is_available and (self.sold_copies < self.total_copies)
    
    @property
    def is_original(self):
        """Check if this is an original artwork (not a print/photo set)"""
        return self.original_artwork is None
    
    @property
    def has_editions(self):
        """Check if this original has prints/photo sets"""
        return self.is_original and self.editions.filter(is_active=True).exists()
    
    @property
    def artwork_age_years(self):
        """Calculate how many years old the artwork is since Jasem made it"""
        from datetime import date
        today = date.today()
        return today.year - self.artwork_creation_date.year


class SculptureImage(TimestampedModel):
    """Multiple angle images for sculptures (max 8)"""
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE, related_name='sculpture_images')
    image = models.ImageField(upload_to='sculptures/angles/')
    angle_description = models.CharField(max_length=100, help_text="e.g., 'Front view', 'Side angle', 'Detail shot'")
    order = models.PositiveIntegerField(default=1, help_text="Display order (1-8)")
    height = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Height in cm (for printed images)")
    width = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Width in cm (for printed images)")
    
    class Meta:
        ordering = ['order']
        unique_together = ['artwork', 'order']
    
    def __str__(self):
        return f"{self.artwork.title} - {self.angle_description}"
    
    @property
    def dimensions_display(self):
        """Return formatted dimensions if available"""
        if self.height and self.width:
            return f"{self.height} × {self.width} cm"
        return "Dimensions not specified"
    
    def save(self, *args, **kwargs):
        # Allow for both sculptures and printed sculpture sets
        if self.artwork.category and 'sculpture' not in self.artwork.category.name.lower():
            raise ValueError("Only sculptures and printed sculpture sets can have multiple angle images")
        super().save(*args, **kwargs)
