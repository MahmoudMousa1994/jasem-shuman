from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Category, Artwork, SculptureImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'name', 'artwork_count', 'add_artwork_button', 'view_artworks_button', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'display_name', 'description']
    ordering = ['name']
    
    def artwork_count(self, obj):
        return obj.artwork_set.count()
    artwork_count.short_description = 'Number of Artworks'
    
    def add_artwork_button(self, obj):
        url = reverse('admin:gallery_artwork_add') + f'?category={obj.id}'
        return format_html(
            '<a class="button" href="{}">+ Add Artwork</a>',
            url
        )
    add_artwork_button.short_description = 'Add'
    
    def view_artworks_button(self, obj):
        url = reverse('admin:gallery_artwork_changelist') + f'?category={obj.id}'
        return format_html(
            '<a class="button" href="{}">View All</a>',
            url
        )
    view_artworks_button.short_description = 'View'


class CategoryListFilter(admin.SimpleListFilter):
    title = 'category'
    parameter_name = 'category'

    def lookups(self, request, model_admin):
        categories = Category.objects.all().order_by('name')
        return [(cat.name, cat.display_name) for cat in categories]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(category__name=self.value())
        return queryset


class SculptureImageInline(admin.TabularInline):
    model = SculptureImage
    extra = 1
    fields = ['image', 'angle_description', 'height', 'width', 'order']
    
    def get_formset(self, request, obj=None, **kwargs):
        # Only show inline for sculptures
        if obj and 'sculpture' not in obj.category.name.lower():
            kwargs['max_num'] = 0
        return super().get_formset(request, obj, **kwargs)


@admin.register(Artwork)
class ArtworkAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'price', 'is_available', 'inventory_status', 
                    'featured', 'created_at']
    list_filter = [CategoryListFilter, 'is_available', 'is_limited_edition', 'featured', 'created_at']
    search_fields = ['title', 'description', 'artist_statement']
    
    inlines = [SculptureImageInline]
    
    def get_fieldsets(self, request, obj=None):
        """Customize fieldsets based on category"""
        
        # Get category from request or object
        category_id = request.GET.get('category')
        category = None
        
        if obj:
            category = obj.category
        elif category_id:
            try:
                category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                pass
        
        # Base fieldsets that all categories have
        fieldsets = [
            ('Basic Information', {
                'fields': ('title', 'category')
            }),
            ('Content', {
                'fields': ('description', 'artist_statement', 'artwork_creation_date')
            }),
        ]
        
        # Determine category type based on category name
        if category:
            cat_name = category.name.lower()
            
            # Original Painting
            if cat_name == 'original_painting':
                fieldsets.append(('Physical Details', {
                    'fields': ('height', 'width'),
                    'description': 'Dimensions for the painting'
                }))
                fieldsets.append(('Media', {
                    'fields': ('main_image', 'artwork_video')
                }))
                fieldsets.append(('Pricing & Availability', {
                    'fields': ('price', 'is_available')
                }))
                fieldsets.append(('Display Options', {
                    'fields': ('is_active', 'featured')
                }))
            
            # Original Sculpture
            elif cat_name == 'original_sculpture':
                fieldsets.append(('Physical Details', {
                    'fields': ('height', 'width', 'depth'),
                    'description': 'All dimensions for the sculpture'
                }))
                fieldsets.append(('Media', {
                    'fields': ('main_image', 'artwork_video')
                }))
                fieldsets.append(('Pricing & Availability', {
                    'fields': ('price', 'is_available')
                }))
                fieldsets.append(('Display Options', {
                    'fields': ('is_active', 'featured')
                }))
                # Sculpture images handled by inline
            
            # Signed Printed Painting
            elif cat_name == 'signed_print_painting':
                fieldsets.append(('Signed Printed Painting Physical Details', {
                    'fields': ('height', 'width'),
                    'description': 'Dimensions for the print'
                }))
                fieldsets.append(('Media', {
                    'fields': ('main_image', 'artwork_video')
                }))
                fieldsets.append(('Limited Edition Settings', {
                    'fields': ('is_limited_edition', 'total_copies', 'sold_copies'),
                    'description': 'Limited edition print settings'
                }))
                fieldsets.append(('Link to Original Artwork', {
                    'fields': ('original_artwork',),
                    'description': 'Select the original painting this print is based on'
                }))
                fieldsets.append(('Pricing & Availability', {
                    'fields': ('price', 'is_available')
                }))
                fieldsets.append(('Display Options', {
                    'fields': ('is_active', 'featured')
                }))
            
            # Signed Set of Printed Images of Sculpture
            elif cat_name == 'signed_print_sculpture':
                fieldsets.append(('Signed Set of Printed Images Details', {
                    'fields': ('height', 'width'),
                    'description': 'Dimensions for each printed image in the set'
                }))
                fieldsets.append(('Media', {
                    'fields': ('main_image', 'artwork_video')
                }))
                fieldsets.append(('Limited Edition Settings', {
                    'fields': ('is_limited_edition', 'total_copies', 'sold_copies'),
                    'description': 'Limited edition settings for the printed set'
                }))
                fieldsets.append(('Link to Original Artwork', {
                    'fields': ('original_artwork',),
                    'description': 'Select the original sculpture this set is based on'
                }))
                fieldsets.append(('Pricing & Availability', {
                    'fields': ('price', 'is_available')
                }))
                fieldsets.append(('Display Options', {
                    'fields': ('is_active', 'featured')
                }))
                # Sculpture images for the printed photos handled by inline
            
            else:
                # Default fallback for any other category
                fieldsets.append(('Physical Details', {
                    'fields': ('height', 'width', 'depth')
                }))
                fieldsets.append(('Media', {
                    'fields': ('main_image', 'artwork_video')
                }))
                fieldsets.append(('Pricing & Availability', {
                    'fields': ('price', 'is_available')
                }))
                fieldsets.append(('Limited Edition Settings', {
                    'fields': ('is_limited_edition', 'total_copies', 'sold_copies'),
                    'classes': ('collapse',)
                }))
                fieldsets.append(('Link to Original', {
                    'fields': ('original_artwork',),
                    'classes': ('collapse',)
                }))
                fieldsets.append(('Display Options', {
                    'fields': ('is_active', 'featured')
                }))
        
        else:
            # No category selected - show all fields
            fieldsets.append(('Physical Details', {
                'fields': ('height', 'width', 'depth')
            }))
            fieldsets.append(('Media', {
                'fields': ('main_image', 'artwork_video')
            }))
            fieldsets.append(('Pricing & Availability', {
                'fields': ('price', 'is_available')
            }))
            fieldsets.append(('Limited Edition Settings', {
                'fields': ('is_limited_edition', 'total_copies', 'sold_copies')
            }))
            fieldsets.append(('Link to Original', {
                'fields': ('original_artwork',)
            }))
            fieldsets.append(('Display Options', {
                'fields': ('is_active', 'featured')
            }))
        
        return fieldsets
    
    def get_inline_instances(self, request, obj=None):
        """Show sculpture images inline only for sculpture categories"""
        inlines = super().get_inline_instances(request, obj)
        
        # Get category from request or object
        category_id = request.GET.get('category')
        category = None
        
        if obj:
            category = obj.category
        elif category_id:
            try:
                category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                pass
        
        # Only show sculpture images for sculpture categories
        if category:
            cat_name = category.name.lower()
            if 'sculpture' not in cat_name:
                return []
        
        return inlines
    
    def get_form(self, request, obj=None, **kwargs):
        """Customize form based on category"""
        form = super().get_form(request, obj, **kwargs)
        
        # Pre-select category if provided in URL
        if not obj and 'category' in request.GET:
            try:
                category_id = int(request.GET['category'])
                form.base_fields['category'].initial = category_id
            except (ValueError, Category.DoesNotExist):
                pass
        
        return form
    
    def inventory_status(self, obj):
        if not obj.is_limited_edition:
            return 'Unique' if obj.is_original else 'Unlimited'
        if obj.total_copies == 0:
            return 'Unlimited'
        return f'{obj.sold_copies}/{obj.total_copies} sold'
    inventory_status.short_description = 'Inventory'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category', 'original_artwork')


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
