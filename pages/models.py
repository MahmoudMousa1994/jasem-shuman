from django.db import models
from django.urls import reverse
from gallery.models import TimestampedModel


class Page(TimestampedModel):
    """Static pages content management"""
    PAGE_TYPES = [
        ('about', 'About Us'),
        ('artist_bio', 'Artist Biography'),
        ('contact', 'Contact Information'),
        ('shipping', 'Shipping Policy'),
        ('returns', 'Returns Policy'),
        ('privacy', 'Privacy Policy'),
        ('terms', 'Terms of Service'),
        ('faq', 'FAQ'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    page_type = models.CharField(max_length=20, choices=PAGE_TYPES, unique=True)
    content = models.TextField()
    meta_description = models.CharField(max_length=160, blank=True, 
                                      help_text="SEO meta description")
    
    # Display options
    is_published = models.BooleanField(default=True)
    show_in_menu = models.BooleanField(default=False)
    menu_order = models.PositiveIntegerField(default=0)
    
    # Featured image (optional)
    featured_image = models.ImageField(upload_to='pages/', null=True, blank=True)
    
    class Meta:
        ordering = ['menu_order', 'title']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('pages:page_detail', kwargs={'slug': self.slug})


class Testimonial(TimestampedModel):
    """Customer testimonials and reviews"""
    name = models.CharField(max_length=200)
    title = models.CharField(max_length=200, blank=True, 
                           help_text="Job title or description (e.g., 'Art Collector')")
    email = models.EmailField(blank=True)
    
    # Testimonial content
    testimonial = models.TextField()
    rating = models.PositiveSmallIntegerField(choices=[
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ], default=5)
    
    # Related purchase (optional)
    related_artwork = models.ForeignKey('gallery.Artwork', on_delete=models.SET_NULL, 
                                      null=True, blank=True)
    
    # Display options
    is_approved = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    
    # Customer photo (optional)
    customer_photo = models.ImageField(upload_to='testimonials/', null=True, blank=True)
    
    class Meta:
        ordering = ['-is_featured', '-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.rating} stars"


class NewsUpdate(TimestampedModel):
    """News updates and announcements"""
    UPDATE_TYPES = [
        ('news', 'General News'),
        ('exhibition', 'Exhibition'),
        ('new_work', 'New Artwork'),
        ('achievement', 'Achievement'),
        ('media', 'Media Coverage'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    update_type = models.CharField(max_length=20, choices=UPDATE_TYPES, default='news')
    summary = models.TextField(max_length=300, help_text="Brief summary for listings")
    content = models.TextField()
    
    # Media
    featured_image = models.ImageField(upload_to='news/', null=True, blank=True)
    image_caption = models.CharField(max_length=200, blank=True)
    
    # SEO
    meta_description = models.CharField(max_length=160, blank=True)
    
    # Publishing
    is_published = models.BooleanField(default=True)
    publish_date = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(default=False)
    
    # Related content
    related_artworks = models.ManyToManyField('gallery.Artwork', blank=True)
    
    class Meta:
        ordering = ['-publish_date']
        verbose_name = "News Update"
        verbose_name_plural = "News Updates"
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('pages:news_detail', kwargs={'slug': self.slug})


class ContactSubmission(TimestampedModel):
    """Contact form submissions"""
    CONTACT_TYPES = [
        ('general', 'General Inquiry'),
        ('commission', 'Commission Request'),
        ('media', 'Media Inquiry'),
        ('exhibition', 'Exhibition Opportunity'),
        ('collaboration', 'Collaboration'),
    ]
    
    # Contact details
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    organization = models.CharField(max_length=200, blank=True)
    
    # Message details
    contact_type = models.CharField(max_length=20, choices=CONTACT_TYPES, default='general')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    
    # Optional file attachment
    attachment = models.FileField(upload_to='contact_attachments/', null=True, blank=True)
    
    # Response tracking
    is_responded = models.BooleanField(default=False)
    response_date = models.DateTimeField(null=True, blank=True)
    admin_notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"


class SocialMediaLink(TimestampedModel):
    """Social media links for the footer"""
    PLATFORMS = [
        ('instagram', 'Instagram'),
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
        ('linkedin', 'LinkedIn'),
        ('youtube', 'YouTube'),
        ('pinterest', 'Pinterest'),
        ('behance', 'Behance'),
        ('artsy', 'Artsy'),
    ]
    
    platform = models.CharField(max_length=20, choices=PLATFORMS, unique=True)
    url = models.URLField()
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['display_order', 'platform']
    
    def __str__(self):
        return f"{self.get_platform_display()}: {self.url}"


class SiteSettings(models.Model):
    """Global site settings"""
    site_name = models.CharField(max_length=200, default="Jasem Shuman Art")
    site_tagline = models.CharField(max_length=200, blank=True, 
                                  default="Contemporary Palestinian Artist")
    
    # Contact information
    contact_email = models.EmailField(default="info@jasemshuman.com")
    contact_phone = models.CharField(max_length=20, blank=True)
    
    # Address
    address_line_1 = models.CharField(max_length=200, blank=True)
    address_line_2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Business settings
    default_currency = models.CharField(max_length=3, default='USD', choices=[
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('GBP', 'British Pound'),
        ('CAD', 'Canadian Dollar'),
    ])
    tax_rate = models.DecimalField(max_digits=5, decimal_places=4, default=0.0000)
    
    # SEO
    meta_description = models.CharField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=200, blank=True)
    
    # Features
    enable_newsletter = models.BooleanField(default=True)
    enable_wishlist = models.BooleanField(default=True)
    enable_reviews = models.BooleanField(default=True)
    
    # Homepage settings
    hero_image = models.ForeignKey('gallery.Artwork', on_delete=models.SET_NULL, 
                                 null=True, blank=True,
                                 help_text="Select artwork to display in homepage hero section")
    
    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"
    
    def __str__(self):
        return "Site Settings"
    
    def save(self, *args, **kwargs):
        # Ensure only one settings instance exists
        if not self.pk and SiteSettings.objects.exists():
            raise ValueError("Only one SiteSettings instance is allowed")
        super().save(*args, **kwargs)
