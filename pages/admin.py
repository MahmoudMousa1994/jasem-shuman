from django.contrib import admin
from django.utils.html import format_html
from .models import (Page, Testimonial, NewsUpdate, ContactSubmission, 
                    SocialMediaLink, SiteSettings, GalleryPageSettings,
                    ArtistEducation, ArtistAward, Exhibition, ArtistPublication)


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ['title', 'page_type', 'is_published', 'show_in_menu', 
                   'menu_order', 'updated_at']
    list_filter = ['page_type', 'is_published', 'show_in_menu', 'created_at']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'page_type', 'content')
        }),
        ('SEO', {
            'fields': ('meta_description', 'featured_image')
        }),
        ('Display Options', {
            'fields': ('is_published', 'show_in_menu', 'menu_order')
        }),
    )


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['name', 'title', 'rating_stars', 'is_approved', 'is_featured', 
                   'related_artwork', 'created_at']
    list_filter = ['rating', 'is_approved', 'is_featured', 'created_at']
    search_fields = ['name', 'title', 'testimonial']
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('name', 'title', 'email', 'customer_photo')
        }),
        ('Testimonial', {
            'fields': ('testimonial', 'rating', 'related_artwork')
        }),
        ('Display Options', {
            'fields': ('is_approved', 'is_featured')
        }),
    )
    
    def rating_stars(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span style="color: #ffc107;">{}</span>', stars)
    rating_stars.short_description = 'Rating'
    
    actions = ['approve_testimonials', 'feature_testimonials']
    
    def approve_testimonials(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} testimonials approved.')
    approve_testimonials.short_description = 'Approve selected testimonials'
    
    def feature_testimonials(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} testimonials featured.')
    feature_testimonials.short_description = 'Feature selected testimonials'


@admin.register(NewsUpdate)
class NewsUpdateAdmin(admin.ModelAdmin):
    list_display = ['title', 'update_type', 'is_published', 'is_featured', 
                   'publish_date']
    list_filter = ['update_type', 'is_published', 'is_featured', 'publish_date']
    search_fields = ['title', 'summary', 'content']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['related_artworks']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'update_type', 'summary', 'content')
        }),
        ('Media', {
            'fields': ('featured_image', 'image_caption')
        }),
        ('SEO', {
            'fields': ('meta_description',)
        }),
        ('Publishing', {
            'fields': ('is_published', 'is_featured')
        }),
        ('Related Content', {
            'fields': ('related_artworks',)
        }),
    )


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'contact_type', 'subject', 'is_responded', 
                   'created_at']
    list_filter = ['contact_type', 'is_responded', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone', 'organization')
        }),
        ('Message', {
            'fields': ('contact_type', 'subject', 'message', 'attachment')
        }),
        ('Response', {
            'fields': ('is_responded', 'response_date', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_responded']
    
    def mark_as_responded(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(is_responded=True, response_date=timezone.now())
        self.message_user(request, f'{updated} submissions marked as responded.')
    mark_as_responded.short_description = 'Mark as responded'


@admin.register(SocialMediaLink)
class SocialMediaLinkAdmin(admin.ModelAdmin):
    list_display = ['platform', 'url', 'is_active', 'display_order']
    list_filter = ['platform', 'is_active']
    ordering = ['display_order', 'platform']


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Site Information', {
            'fields': ('site_name', 'site_tagline')
        }),
        ('Contact Information', {
            'fields': ('contact_email', 'contact_phone')
        }),
        ('Address', {
            'fields': ('address_line_1', 'address_line_2', 'city', 'state', 
                      'postal_code', 'country')
        }),
        ('Business Settings', {
            'fields': ('default_currency', 'tax_rate')
        }),
        ('SEO', {
            'fields': ('meta_description', 'meta_keywords')
        }),
        ('Features', {
            'fields': ('enable_newsletter', 'enable_wishlist', 'enable_reviews')
        }),
        ('Homepage Settings', {
            'fields': ('hero_image',)
        }),
    )
    
    def has_add_permission(self, request):
        # Prevent multiple instances
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of settings
        return False


@admin.register(GalleryPageSettings)
class GalleryPageSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Hero Section', {
            'fields': ('hero_title', 'hero_subtitle', 'hero_description')
        }),
        ('Featured Section', {
            'fields': ('show_featured_section', 'featured_section_title', 
                      'featured_section_subtitle', 'featured_artworks_count')
        }),
        ('Recent Works Section', {
            'fields': ('show_recent_section', 'recent_section_title', 
                      'recent_section_subtitle', 'recent_artworks_count')
        }),
        ('Categories Section', {
            'fields': ('show_categories_section', 'categories_section_title', 
                      'categories_section_subtitle')
        }),
    )
    
    def has_add_permission(self, request):
        # Prevent multiple instances
        return not GalleryPageSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of settings
        return False


@admin.register(ArtistEducation)
class ArtistEducationAdmin(admin.ModelAdmin):
    list_display = ['degree_title', 'institution', 'location', 'year_range', 'display_order']
    list_filter = ['year_start', 'year_end']
    search_fields = ['degree_title', 'institution', 'location']
    ordering = ['display_order', '-year_start']
    
    fieldsets = (
        ('Education Details', {
            'fields': ('degree_title', 'institution', 'location')
        }),
        ('Time Period', {
            'fields': ('year_start', 'year_end')
        }),
        ('Additional Information', {
            'fields': ('description', 'display_order')
        }),
    )
    
    def year_range(self, obj):
        return f"{obj.year_start}-{obj.year_end if obj.year_end else 'Present'}"
    year_range.short_description = 'Years'


@admin.register(ArtistAward)
class ArtistAwardAdmin(admin.ModelAdmin):
    list_display = ['award_title', 'organization', 'year', 'has_certificate', 'display_order']
    list_filter = ['year']
    search_fields = ['award_title', 'organization']
    ordering = ['display_order', '-year']
    
    fieldsets = (
        ('Award Details', {
            'fields': ('award_title', 'organization', 'year')
        }),
        ('Additional Information', {
            'fields': ('description', 'certificate_image', 'display_order')
        }),
    )
    
    def has_certificate(self, obj):
        if obj.certificate_image:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')
    has_certificate.short_description = 'Certificate'


@admin.register(Exhibition)
class ExhibitionAdmin(admin.ModelAdmin):
    list_display = ['title', 'exhibition_type', 'venue', 'location_short', 'start_date', 'is_featured']
    list_filter = ['exhibition_type', 'is_featured', 'start_date', 'country']
    search_fields = ['title', 'venue', 'city', 'country', 'description']
    filter_horizontal = ['featured_artworks']
    ordering = ['-start_date', 'display_order']
    
    fieldsets = (
        ('Event Information', {
            'fields': ('title', 'exhibition_type', 'role')
        }),
        ('Location', {
            'fields': ('venue', 'city', 'country')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date')
        }),
        ('Details', {
            'fields': ('description', 'website_url', 'poster_image')
        }),
        ('Related Content', {
            'fields': ('featured_artworks',)
        }),
        ('Display Options', {
            'fields': ('is_featured', 'display_order')
        }),
    )
    
    def location_short(self, obj):
        return f"{obj.city}, {obj.country}"
    location_short.short_description = 'Location'
    
    actions = ['mark_as_featured']
    
    def mark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} exhibitions marked as featured.')
    mark_as_featured.short_description = 'Mark as featured'


@admin.register(ArtistPublication)
class ArtistPublicationAdmin(admin.ModelAdmin):
    list_display = ['title', 'publication_type', 'publication_name', 'publication_date', 
                   'has_url', 'has_pdf']
    list_filter = ['publication_type', 'publication_date']
    search_fields = ['title', 'publication_name', 'author', 'description']
    ordering = ['-publication_date', 'display_order']
    
    fieldsets = (
        ('Publication Details', {
            'fields': ('title', 'publication_type', 'publication_name', 'author', 'publication_date')
        }),
        ('Content', {
            'fields': ('description', 'url', 'pdf_file', 'cover_image')
        }),
        ('Display Options', {
            'fields': ('display_order',)
        }),
    )
    
    def has_url(self, obj):
        if obj.url:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')
    has_url.short_description = 'Online'
    
    def has_pdf(self, obj):
        if obj.pdf_file:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')
    has_pdf.short_description = 'PDF'

