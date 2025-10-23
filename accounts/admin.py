from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import UserProfile, WishlistItem, CustomerInquiry


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fieldsets = (
        ('Contact Information', {
            'fields': ('phone', 'date_of_birth')
        }),
        ('Address', {
            'fields': ('address_line_1', 'address_line_2', 'city', 'state', 
                      'postal_code', 'country')
        }),
        ('Preferences', {
            'fields': ('newsletter_subscription', 'email_notifications', 'preferred_currency')
        }),
        ('Profile', {
            'fields': ('profile_image', 'bio')
        }),
    )


class ExtendedUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = UserAdmin.list_display + ('profile_complete', 'newsletter_subscriber')
    
    def profile_complete(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.has_complete_address
        return False
    profile_complete.boolean = True
    profile_complete.short_description = 'Profile Complete'
    
    def newsletter_subscriber(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.newsletter_subscription
        return False
    newsletter_subscriber.boolean = True
    newsletter_subscriber.short_description = 'Newsletter'


# Unregister the default User admin and register our extended version
admin.site.unregister(User)
admin.site.register(User, ExtendedUserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'phone', 'city', 'country', 
                   'newsletter_subscription', 'created_at']
    list_filter = ['newsletter_subscription', 'email_notifications', 
                  'preferred_currency', 'country', 'created_at']
    search_fields = ['user__username', 'user__email', 'user__first_name', 
                    'user__last_name', 'phone', 'city']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Contact Information', {
            'fields': ('phone', 'date_of_birth')
        }),
        ('Address', {
            'fields': ('address_line_1', 'address_line_2', 'city', 'state', 
                      'postal_code', 'country')
        }),
        ('Preferences', {
            'fields': ('newsletter_subscription', 'email_notifications', 'preferred_currency')
        }),
        ('Profile', {
            'fields': ('profile_image', 'bio')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ['user', 'artwork', 'item_type', 'artwork_price', 'created_at']
    list_filter = ['item_type', 'created_at', 'artwork__category']
    search_fields = ['user__username', 'artwork__title']
    
    def artwork_price(self, obj):
        if obj.item_type == 'original':
            return f"${obj.artwork.original_price}"
        else:
            return f"${obj.artwork.second_option_price}"
    artwork_price.short_description = 'Price'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'artwork')


@admin.register(CustomerInquiry)
class CustomerInquiryAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'inquiry_type', 'subject', 'status', 
                   'related_artwork', 'created_at']
    list_filter = ['inquiry_type', 'status', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone', 'user')
        }),
        ('Inquiry Details', {
            'fields': ('inquiry_type', 'subject', 'message', 'related_artwork')
        }),
        ('Response', {
            'fields': ('status', 'admin_response', 'response_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        # Automatically set response_date when status changes to resolved/closed
        if change and obj.status in ['resolved', 'closed'] and not obj.response_date:
            from django.utils import timezone
            obj.response_date = timezone.now()
        super().save_model(request, obj, form, change)
    
    actions = ['mark_as_resolved', 'mark_as_in_progress']
    
    def mark_as_resolved(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='resolved', response_date=timezone.now())
        self.message_user(request, f'{updated} inquiries marked as resolved.')
    mark_as_resolved.short_description = 'Mark selected inquiries as resolved'
    
    def mark_as_in_progress(self, request, queryset):
        updated = queryset.update(status='in_progress')
        self.message_user(request, f'{updated} inquiries marked as in progress.')
    mark_as_in_progress.short_description = 'Mark selected inquiries as in progress'
