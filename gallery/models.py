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
    """Art categories: painting, sculpture"""
    CATEGORY_CHOICES = [
        ('painting', 'Painting'),
        ('sculpture', 'Sculpture'),
    ]
    
    name = models.CharField(max_length=20, choices=CATEGORY_CHOICES, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.get_name_display()


class Artwork(TimestampedModel):
    """Main artwork model with dual pricing system"""
    
    # Basic artwork info
    title = models.CharField(max_length=200)
    description = models.TextField()
    artist_statement = models.TextField(help_text="Artist's statement about this piece")
    
    # When Jasem actually created this artwork
    artwork_creation_date = models.DateField(help_text="When Jasem created this artwork")
    
    # Original artwork dimensions
    original_height = models.DecimalField(max_digits=8, decimal_places=2, help_text="Original height in cm")
    original_width = models.DecimalField(max_digits=8, decimal_places=2, help_text="Original width in cm")
    original_depth = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Original depth in cm (for sculptures)")
    
    # Print/Photo set dimensions
    print_height = models.DecimalField(max_digits=8, decimal_places=2, help_text="Print/photo height in cm")
    print_width = models.DecimalField(max_digits=8, decimal_places=2, help_text="Print/photo width in cm")
    
    # Media files
    main_image = models.ImageField(upload_to='artworks/')
    artwork_video = models.FileField(upload_to='artworks/videos/', null=True, blank=True, help_text="Video of the artwork")
    
    # Pricing & inventory
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    original_available = models.BooleanField(default=True)
    second_option_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price for prints/photo sets")
    total_second_option_copies = models.PositiveIntegerField(default=50)
    sold_second_option_copies = models.PositiveIntegerField(default=0)
    
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
    def original_dimensions_display(self):
        """Format original dimensions for display"""
        if self.category.name == 'sculpture' and self.original_depth:
            return f"{self.original_height} × {self.original_width} × {self.original_depth} cm"
        return f"{self.original_height} × {self.original_width} cm"
    
    @property
    def print_dimensions_display(self):
        """Format print/photo dimensions for display"""
        return f"{self.print_height} × {self.print_width} cm"
    
    @property
    def remaining_second_option(self):
        """Calculate remaining copies of second option"""
        return self.total_second_option_copies - self.sold_second_option_copies
    
    @property
    def second_option_available(self):
        """Check if second option is available"""
        return self.remaining_second_option > 0
    
    @property
    def second_option_name(self):
        """Get the name of the second option based on category"""
        if self.category.name == 'painting':
            return 'Print Copy'
        elif self.category.name == 'sculpture':
            return 'Signed Photo Set'
        return 'Second Option'
    
    @property
    def has_video(self):
        """Check if artwork has a video"""
        return bool(self.artwork_video)
    
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
    
    class Meta:
        ordering = ['order']
        unique_together = ['artwork', 'order']
    
    def __str__(self):
        return f"{self.artwork.title} - {self.angle_description}"
    
    def save(self, *args, **kwargs):
        # Ensure only sculptures can have multiple images
        if self.artwork.category.name != 'sculpture':
            raise ValueError("Only sculptures can have multiple angle images")
        super().save(*args, **kwargs)
