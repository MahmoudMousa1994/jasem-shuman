from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Artwork, Category


def gallery_home(request):
    """Homepage with featured artworks and gallery overview"""
    # Get featured artworks
    featured_artworks = Artwork.objects.filter(featured=True, is_active=True)[:6]
    
    # Get recent artworks
    recent_artworks = Artwork.objects.filter(is_active=True).order_by('-created_at')[:8]
    
    # Get categories with artwork counts
    categories = Category.objects.all()
    category_data = []
    for category in categories:
        artwork_count = category.artwork_set.filter(is_active=True).count()
        if artwork_count > 0:
            # Get a sample artwork for category image
            sample_artwork = category.artwork_set.filter(is_active=True).first()
            category_data.append({
                'category': category,
                'count': artwork_count,
                'sample_artwork': sample_artwork
            })
    
    context = {
        'featured_artworks': featured_artworks,
        'recent_artworks': recent_artworks,
        'categories': category_data,
        'page_title': 'Jasem Shuman - Contemporary Palestinian Artist',
        'meta_description': 'Explore the contemporary Palestinian artwork of Jasem Shuman. Original paintings and sculptures available for purchase.',
    }
    return render(request, 'gallery/home.html', context)


def artwork_detail(request, pk):
    """Detailed view of a specific artwork"""
    artwork = get_object_or_404(Artwork, pk=pk, is_active=True)
    
    # Get related artworks from same category (excluding current)
    related_artworks = Artwork.objects.filter(
        category=artwork.category, 
        is_active=True
    ).exclude(pk=artwork.pk)[:4]
    
    # Get sculpture images if it's a sculpture
    sculpture_images = []
    if artwork.category.name == 'sculpture':
        sculpture_images = artwork.sculpture_images.all().order_by('order')
    
    context = {
        'artwork': artwork,
        'related_artworks': related_artworks,
        'sculpture_images': sculpture_images,
        'page_title': f'{artwork.title} - Jasem Shuman Art',
        'meta_description': f'{artwork.description[:150]}...',
    }
    return render(request, 'gallery/artwork_detail.html', context)


def category_view(request, category_name):
    """View artworks by category (paintings or sculptures)"""
    category = get_object_or_404(Category, name=category_name)
    
    # Get all artworks in this category
    artworks_list = Artwork.objects.filter(
        category=category, 
        is_active=True
    ).order_by('-featured', '-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        artworks_list = artworks_list.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(artist_statement__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(artworks_list, 12)  # 12 artworks per page
    page_number = request.GET.get('page')
    artworks = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'artworks': artworks,
        'search_query': search_query,
        'page_title': f'{category.get_name_display()} - Jasem Shuman Art',
        'meta_description': f'Browse {category.get_name_display().lower()} by Palestinian artist Jasem Shuman.',
    }
    return render(request, 'gallery/category.html', context)


def artwork_api(request):
    """API endpoint for AJAX filtering of artworks"""
    category_name = request.GET.get('category', '')
    search_query = request.GET.get('search', '')
    
    artworks = Artwork.objects.filter(is_active=True)
    
    if category_name:
        artworks = artworks.filter(category__name=category_name)
    
    if search_query:
        artworks = artworks.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Prepare JSON response
    artwork_data = []
    for artwork in artworks[:20]:  # Limit to 20 results
        artwork_data.append({
            'id': artwork.id,
            'title': artwork.title,
            'image_url': artwork.main_image.url if artwork.main_image else '',
            'original_price': str(artwork.original_price),
            'second_option_price': str(artwork.second_option_price),
            'category': artwork.category.get_name_display(),
            'url': f'/artwork/{artwork.id}/',
            'original_available': artwork.original_available,
            'second_option_available': artwork.second_option_available,
            'second_option_name': artwork.second_option_name,
        })
    
    return JsonResponse({
        'artworks': artwork_data,
        'count': len(artwork_data)
    })
