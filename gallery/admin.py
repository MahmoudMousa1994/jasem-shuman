from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Artwork, SculptureImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'artwork_count', 'created_at']
    list_filter = ['name', 'created_at']
    search_fields = ['name', 'description']
    
    def artwork_count(self, obj):
        return obj.artwork_set.count()
    artwork_count.short_description = 'Number of Artworks'


class SculptureImageInline(admin.TabularInline):
    model = SculptureImage
    extra = 1
    fields = ['image', 'angle_description', 'order']
    
    def get_formset(self, request, obj=None, **kwargs):
        # Only show inline for sculptures
        if obj and obj.category.name != 'sculpture':
            kwargs['max_num'] = 0
        return super().get_formset(request, obj, **kwargs)


@admin.register(Artwork)
class ArtworkAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'original_price', 'second_option_price', 
                   'original_available', 'featured', 'created_at']
    list_filter = ['category', 'original_available', 'featured', 'created_at']
    search_fields = ['title', 'description', 'artist_statement']
    
    inlines = [SculptureImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'category', 'description', 'artist_statement', 'artwork_creation_date')
        }),
        ('Physical Details', {
            'fields': ('original_height', 'original_width', 'original_depth', 
                      'print_height', 'print_width')
        }),
        ('Media', {
            'fields': ('main_image', 'artwork_video')
        }),
        ('Pricing & Availability', {
            'fields': ('original_price', 'original_available', 'second_option_price', 
                      'total_second_option_copies', 'sold_second_option_copies')
        }),
        ('Display Options', {
            'fields': ('is_active', 'featured')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category')


@admin.register(SculptureImage)
class SculptureImageAdmin(admin.ModelAdmin):
    list_display = ['artwork', 'angle_description', 'order', 'image_preview']
    list_filter = ['artwork__category']
    search_fields = ['artwork__title', 'angle_description']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = 'Preview'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('artwork')


# Customize admin site headers
admin.site.site_header = "Jasem Shuman Art Administration"
admin.site.site_title = "Jasem Shuman Art Admin"
admin.site.index_title = "Welcome to Jasem Shuman Art Administration"
