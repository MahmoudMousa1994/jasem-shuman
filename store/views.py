from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Cart, CartItem, Order
from gallery.models import Artwork, Category


def store_home(request):
    """Store homepage with featured artworks and categories"""
    featured_artworks = Artwork.objects.filter(featured=True, original_available=True)[:8]
    categories = Category.objects.all()
    
    context = {
        'page_title': 'Store - Jasem Shuman Art',
        'featured_artworks': featured_artworks,
        'categories': categories,
    }
    return render(request, 'store/home.html', context)


def cart_view(request):
    """Shopping cart view"""
    # Placeholder for cart functionality
    context = {
        'page_title': 'Shopping Cart - Jasem Shuman Art',
    }
    return render(request, 'store/cart.html', context)


def add_to_cart(request):
    """Add item to cart (AJAX)"""
    # Placeholder for add to cart functionality
    return JsonResponse({'success': True, 'message': 'Item added to cart'})


@login_required
def checkout(request):
    """Checkout process"""
    # Placeholder for checkout functionality
    context = {
        'page_title': 'Checkout - Jasem Shuman Art',
    }
    return render(request, 'store/checkout.html', context)


@login_required
def order_history(request):
    """User order history"""
    # Placeholder for order history
    context = {
        'page_title': 'Order History - Jasem Shuman Art',
    }
    return render(request, 'store/order_history.html', context)


@login_required
def order_detail(request, order_id):
    """Individual order detail"""
    # Placeholder for order detail
    context = {
        'page_title': f'Order #{order_id} - Jasem Shuman Art',
    }
    return render(request, 'store/order_detail.html', context)
