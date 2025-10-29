from django.contrib import admin
from django.utils.html import format_html
from .models import (Page, Testimonial, NewsUpdate, ContactSubmission, 
                    SocialMediaLink, SiteSettings)


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
