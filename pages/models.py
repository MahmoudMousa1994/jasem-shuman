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
    contact_email = models.EmailField(default="jasem_403@hotmail.com")
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


class GalleryPageSettings(models.Model):
    """Gallery homepage content settings"""
    hero_title = models.CharField(max_length=200, default="JASEM SHUMAN")
    hero_subtitle = models.CharField(max_length=200, default="Artist")
    hero_description = models.TextField(
        default="Contemporary Palestinian artist exploring the intersection of traditional techniques and modern expression.",
        help_text="Description text shown below hero image"
    )
    
    # Section headings
    featured_section_title = models.CharField(max_length=100, default="Featured Artworks")
    featured_section_subtitle = models.CharField(max_length=200, blank=True)
    
    recent_section_title = models.CharField(max_length=100, default="Recent Works")
    recent_section_subtitle = models.CharField(max_length=200, blank=True)
    
    categories_section_title = models.CharField(max_length=100, default="Explore by Category")
    categories_section_subtitle = models.CharField(max_length=200, blank=True)
    
    # Display options
    show_featured_section = models.BooleanField(default=True)
    show_recent_section = models.BooleanField(default=True)
    show_categories_section = models.BooleanField(default=True)
    
    # Number of items to display
    featured_artworks_count = models.PositiveIntegerField(default=6, help_text="Number of featured artworks to display")
    recent_artworks_count = models.PositiveIntegerField(default=8, help_text="Number of recent artworks to display")
    
    class Meta:
        verbose_name = "Gallery Page Settings"
        verbose_name_plural = "Gallery Page Settings"
    
    def __str__(self):
        return "Gallery Page Settings"
    
    def save(self, *args, **kwargs):
        # Ensure only one settings instance exists
        if not self.pk and GalleryPageSettings.objects.exists():
            raise ValueError("Only one GalleryPageSettings instance is allowed")
        super().save(*args, **kwargs)


class ArtistEducation(TimestampedModel):
    """Artist's education and degrees"""
    degree_title = models.CharField(max_length=200, help_text="e.g., Bachelor of Fine Arts")
    institution = models.CharField(max_length=200, help_text="University or institution name")
    location = models.CharField(max_length=200, blank=True, help_text="City, Country")
    year_start = models.PositiveIntegerField(help_text="Year started")
    year_end = models.PositiveIntegerField(null=True, blank=True, help_text="Year completed (leave blank if ongoing)")
    description = models.TextField(blank=True, help_text="Additional details about this education")
    display_order = models.PositiveIntegerField(default=0, help_text="Order to display (lower numbers first)")
    
    class Meta:
        ordering = ['-year_start', 'display_order']
        verbose_name = "Artist Education"
        verbose_name_plural = "Artist Education"
    
    def __str__(self):
        year_range = f"{self.year_start}-{self.year_end if self.year_end else 'Present'}"
        return f"{self.degree_title} - {self.institution} ({year_range})"


class ArtistAward(TimestampedModel):
    """Artist's awards and recognitions"""
    award_title = models.CharField(max_length=200, help_text="Name of the award")
    organization = models.CharField(max_length=200, help_text="Organization that gave the award")
    year = models.PositiveIntegerField(help_text="Year received")
    description = models.TextField(blank=True, help_text="Details about the award")
    certificate_image = models.ImageField(upload_to='awards/', null=True, blank=True)
    display_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-year', 'display_order']
        verbose_name = "Artist Award"
        verbose_name_plural = "Artist Awards"
    
    def __str__(self):
        return f"{self.award_title} ({self.year})"


class Exhibition(TimestampedModel):
    """Artist exhibitions, conventions, and workshops"""
    EXHIBITION_TYPES = [
        ('solo', 'Solo Exhibition'),
        ('group', 'Group Exhibition'),
        ('convention', 'Art Convention'),
        ('workshop', 'Workshop'),
        ('fair', 'Art Fair'),
        ('residency', 'Artist Residency'),
        ('other', 'Other Event'),
    ]
    
    title = models.CharField(max_length=200, help_text="Exhibition or event name")
    exhibition_type = models.CharField(max_length=20, choices=EXHIBITION_TYPES, default='group')
    venue = models.CharField(max_length=200, help_text="Gallery, museum, or location name")
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    
    # Date range
    start_date = models.DateField(help_text="Event start date")
    end_date = models.DateField(null=True, blank=True, help_text="Event end date (leave blank for one-day events)")
    
    # Details
    description = models.TextField(blank=True, help_text="Description of the exhibition or event")
    role = models.CharField(max_length=200, blank=True, help_text="Your role (e.g., 'Featured Artist', 'Workshop Instructor')")
    
    # Media
    poster_image = models.ImageField(upload_to='exhibitions/', null=True, blank=True)
    website_url = models.URLField(blank=True, help_text="Exhibition website or event page")
    
    # Related artworks
    featured_artworks = models.ManyToManyField('gallery.Artwork', blank=True, 
                                              help_text="Artworks shown in this exhibition")
    
    # Display options
    is_featured = models.BooleanField(default=False, help_text="Show prominently on gallery page")
    display_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-start_date', 'display_order']
        verbose_name = "Exhibition/Event"
        verbose_name_plural = "Exhibitions & Events"
    
    def __str__(self):
        return f"{self.title} - {self.venue} ({self.start_date.year})"
    
    @property
    def date_display(self):
        """Format date range for display"""
        if self.end_date:
            if self.start_date.year == self.end_date.year:
                if self.start_date.month == self.end_date.month:
                    return f"{self.start_date.strftime('%B %d')}-{self.end_date.strftime('%d, %Y')}"
                return f"{self.start_date.strftime('%B %d')} - {self.end_date.strftime('%B %d, %Y')}"
            return f"{self.start_date.strftime('%B %Y')} - {self.end_date.strftime('%B %Y')}"
        return self.start_date.strftime('%B %d, %Y')
    
    @property
    def location_display(self):
        """Format location for display"""
        return f"{self.city}, {self.country}"


class ArtistPublication(TimestampedModel):
    """Publications, press, and media coverage"""
    PUBLICATION_TYPES = [
        ('article', 'Magazine/Newspaper Article'),
        ('interview', 'Interview'),
        ('review', 'Art Review'),
        ('catalog', 'Exhibition Catalog'),
        ('book', 'Book Feature'),
        ('online', 'Online Publication'),
    ]
    
    title = models.CharField(max_length=200, help_text="Article or publication title")
    publication_type = models.CharField(max_length=20, choices=PUBLICATION_TYPES, default='article')
    publication_name = models.CharField(max_length=200, help_text="Magazine, newspaper, or website name")
    author = models.CharField(max_length=200, blank=True, help_text="Author or journalist name")
    publication_date = models.DateField(help_text="Date published")
    
    description = models.TextField(blank=True, help_text="Brief description or excerpt")
    url = models.URLField(blank=True, help_text="Link to online article")
    pdf_file = models.FileField(upload_to='publications/', null=True, blank=True, 
                                help_text="Upload PDF of the article")
    cover_image = models.ImageField(upload_to='publications/', null=True, blank=True)
    
    display_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-publication_date', 'display_order']
        verbose_name = "Publication/Press"
        verbose_name_plural = "Publications & Press"
    
    def __str__(self):
        return f"{self.title} - {self.publication_name} ({self.publication_date.year})"
