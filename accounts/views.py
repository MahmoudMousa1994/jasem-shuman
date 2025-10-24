from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import JsonResponse
from .models import UserProfile, WishlistItem
from .forms import UserProfileForm, CustomUserCreationForm
from gallery.models import Artwork


def logout_view(request):
    """Custom logout view that handles both GET and POST"""
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'You have been successfully logged out.')
        return redirect('gallery:home')
    
    # For GET requests, show confirmation page
    return render(request, 'accounts/logout.html')


def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Authenticate the user with our custom backend
            authenticated_user = authenticate(
                request, 
                username=user.email,  # Using email as username
                password=form.cleaned_data['password1'],
                backend='accounts.backends.EmailBackend'
            )
            if authenticated_user:
                login(request, authenticated_user, backend='accounts.backends.EmailBackend')
                messages.success(request, 'Welcome to Jasem Shuman Art! Your account has been created.')
                return redirect('gallery:home')
    else:
        form = CustomUserCreationForm()
    
    context = {
        'form': form,
        'page_title': 'Create Account - Jasem Shuman Art',
    }
    return render(request, 'accounts/register.html', context)


@login_required
def profile(request):
    """User profile view"""
    profile = request.user.profile
    recent_orders = []  # Will implement with store app
    wishlist_items = WishlistItem.objects.filter(user=request.user)[:5]
    
    context = {
        'profile': profile,
        'recent_orders': recent_orders,
        'wishlist_items': wishlist_items,
        'page_title': f'{request.user.username} - Profile',
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile(request):
    """Edit user profile view"""
    profile = request.user.profile
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=profile)
    
    context = {
        'form': form,
        'page_title': 'Edit Profile - Jasem Shuman Art',
    }
    return render(request, 'accounts/edit_profile.html', context)


@login_required
def wishlist(request):
    """User wishlist view"""
    wishlist_items = WishlistItem.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'wishlist_items': wishlist_items,
        'page_title': 'My Wishlist - Jasem Shuman Art',
    }
    return render(request, 'accounts/wishlist.html', context)


@login_required
def add_to_wishlist(request, artwork_id):
    """Add artwork to wishlist (AJAX)"""
    if request.method == 'POST':
        artwork = get_object_or_404(Artwork, id=artwork_id)
        item_type = request.POST.get('item_type', 'original')
        
        # Check if already in wishlist
        existing = WishlistItem.objects.filter(
            user=request.user,
            artwork=artwork,
            item_type=item_type
        ).first()
        
        if existing:
            return JsonResponse({
                'success': False,
                'message': 'This item is already in your wishlist.'
            })
        
        # Add to wishlist
        WishlistItem.objects.create(
            user=request.user,
            artwork=artwork,
            item_type=item_type
        )
        
        return JsonResponse({
            'success': True,
            'message': f'{artwork.title} added to your wishlist.'
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid request.'})


@login_required
def remove_from_wishlist(request, item_id):
    """Remove item from wishlist"""
    item = get_object_or_404(WishlistItem, id=item_id, user=request.user)
    artwork_title = item.artwork.title
    item.delete()
    
    messages.success(request, f'{artwork_title} removed from your wishlist.')
    return redirect('accounts:wishlist')
