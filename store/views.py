from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import models
from decimal import Decimal
from .models import Cart, CartItem, Order, OrderItem, ShippingAddress, PaymentInfo
from gallery.models import Artwork, Category
import json


# Debug view to check cart state
def debug_cart(request):
    """Debug view to check cart state"""
    debug_info = {
        'user_authenticated': request.user.is_authenticated,
        'session_key': request.session.session_key,
        'cart_count_from_context': 0,
        'carts_in_db': [],
        'cart_items': []
    }
    
    # Get cart count from context processor
    from .context_processors import cart_context
    context = cart_context(request)
    debug_info['cart_count_from_context'] = context.get('cart_count', 0)
    
    # Get all carts
    for cart in Cart.objects.all():
        debug_info['carts_in_db'].append({
            'id': cart.id,
            'user': str(cart.user) if cart.user else None,
            'session_key': cart.session_key,
            'total_items': cart.total_items,
            'created_at': str(cart.created_at)
        })
    
    # Get all cart items
    for item in CartItem.objects.all():
        debug_info['cart_items'].append({
            'id': item.id,
            'cart_id': item.cart.id,
            'artwork': str(item.artwork),
            'item_type': item.item_type,
            'quantity': item.quantity
        })
    
    return JsonResponse(debug_info, json_dumps_params={'indent': 2})


def get_cart_count(request):
    """AJAX endpoint to get current cart count"""
    from .context_processors import cart_context
    context = cart_context(request)
    return JsonResponse({
        'cart_count': context.get('cart_count', 0)
    })


def store_home(request):
    """Store homepage with categories"""
    # Get all categories
    categories = Category.objects.all()
    
    # Get artwork counts and sample artworks for each category
    category_data = []
    for category in categories:
        # Get available artworks for this category
        available_artworks = Artwork.objects.filter(
            category=category
        ).filter(
            models.Q(original_available=True) | 
            models.Q(total_second_option_copies__gt=models.F('sold_second_option_copies'))
        )
        
        artwork_count = available_artworks.count()
        sample_artwork = available_artworks.first()  # Get first artwork as sample
        
        category_data.append({
            'category': category,
            'artwork_count': artwork_count,
            'sample_artwork': sample_artwork
        })
    
    context = {
        'page_title': 'Store - Jasem Shuman Art',
        'categories': category_data,
    }
    return render(request, 'store/home.html', context)


def category_view(request, category_name):
    """Display artworks for a specific category"""
    # Get the category
    category = get_object_or_404(Category, name=category_name)
    
    # Get artworks for this category that are available
    artworks = Artwork.objects.filter(
        category=category
    ).filter(
        models.Q(original_available=True) | 
        models.Q(total_second_option_copies__gt=models.F('sold_second_option_copies'))
    ).order_by('title')
    
    context = {
        'page_title': f'{category.get_name_display()} - Jasem Shuman Art',
        'category': category,
        'artworks': artworks,
        'artwork_count': artworks.count(),
    }
    return render(request, 'store/category.html', context)


def cart_view(request):
    """Shopping cart view"""
    cart_items = []
    cart_total = 0
    cart_count = 0
    
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_items = cart.items.all()
            cart_total = cart.total_price
            cart_count = cart.total_items
        except Cart.DoesNotExist:
            pass
    else:
        # For anonymous users, check session-based cart
        if request.session.session_key:
            try:
                cart = Cart.objects.get(session_key=request.session.session_key)
                cart_items = cart.items.all()
                cart_total = cart.total_price
                cart_count = cart.total_items
            except Cart.DoesNotExist:
                pass
    
    context = {
        'page_title': 'Shopping Cart - Jasem Shuman Art',
        'cart_items': cart_items,
        'cart_total': cart_total,
        'cart_count': cart_count,
    }
    return render(request, 'store/cart.html', context)


@require_POST
def add_to_cart(request):
    """Add item to cart (AJAX)"""
    try:
        # Parse JSON data
        data = json.loads(request.body)
        artwork_id = data.get('artwork_id')
        item_type = data.get('item_type', 'original')
        quantity = int(data.get('quantity', 1))
        
        # Get artwork
        artwork = get_object_or_404(Artwork, id=artwork_id)
        
        # Check availability
        if item_type == 'original' and not artwork.original_available:
            return JsonResponse({
                'success': False, 
                'message': 'Original artwork is no longer available'
            })
        elif item_type != 'original' and not artwork.second_option_available:
            return JsonResponse({
                'success': False, 
                'message': f'{artwork.second_option_name} is no longer available'
            })
        
        # Get or create cart
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
        else:
            # For anonymous users, use session
            if not request.session.session_key:
                request.session.create()
            cart, created = Cart.objects.get_or_create(session_key=request.session.session_key)
        
        # Get or create cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            artwork=artwork,
            item_type=item_type,
            defaults={'quantity': quantity}
        )
        
        if not created:
            # Item already exists, update quantity
            cart_item.quantity += quantity
            cart_item.save()
            message = f'Updated {artwork.title} quantity in cart'
        else:
            message = f'{artwork.title} added to cart'
        
        # Return success response
        return JsonResponse({
            'success': True,
            'message': message,
            'cart_total_items': cart.total_items,
            'cart_total_price': float(cart.total_price) if cart.total_price else 0
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid request data'
        })
    except Artwork.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Artwork not found'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'An error occurred while adding to cart'
        })


@require_POST
def update_cart_item(request):
    """Update cart item quantity (AJAX)"""
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        quantity = int(data.get('quantity', 1))
        
        # Get cart item
        cart_item = get_object_or_404(CartItem, id=item_id)
        
        # Verify ownership
        if request.user.is_authenticated:
            if cart_item.cart.user != request.user:
                return JsonResponse({'success': False, 'message': 'Unauthorized'})
        else:
            if cart_item.cart.session_key != request.session.session_key:
                return JsonResponse({'success': False, 'message': 'Unauthorized'})
        
        # Update quantity
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Cart updated',
                'item_total': float(cart_item.total_price),
                'cart_total': float(cart_item.cart.total_price),
                'cart_total_items': cart_item.cart.total_items
            })
        else:
            return JsonResponse({'success': False, 'message': 'Invalid quantity'})
            
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid request data'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'An error occurred'})


@require_POST 
def remove_cart_item(request):
    """Remove item from cart (AJAX)"""
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        
        # Get cart item
        cart_item = get_object_or_404(CartItem, id=item_id)
        
        # Verify ownership
        if request.user.is_authenticated:
            if cart_item.cart.user != request.user:
                return JsonResponse({'success': False, 'message': 'Unauthorized'})
        else:
            if cart_item.cart.session_key != request.session.session_key:
                return JsonResponse({'success': False, 'message': 'Unauthorized'})
        
        # Get cart for response
        cart = cart_item.cart
        
        # Remove item
        cart_item.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Item removed from cart',
            'cart_total': float(cart.total_price) if cart.total_price else 0,
            'cart_total_items': cart.total_items
        })
            
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid request data'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'An error occurred'})


@login_required
def checkout(request):
    """Checkout process"""
    # Get user's cart
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.all()
        
        if not cart_items.exists():
            messages.warning(request, 'Your cart is empty. Please add items before checkout.')
            return redirect('store:cart')
            
    except Cart.DoesNotExist:
        messages.warning(request, 'Your cart is empty. Please add items before checkout.')
        return redirect('store:cart')
    
    if request.method == 'POST':
        # Process checkout form
        try:
            # Extract form data
            shipping_data = {
                'first_name': request.POST.get('first_name', '').strip(),
                'last_name': request.POST.get('last_name', '').strip(),
                'email': request.POST.get('email', '').strip(),
                'phone': request.POST.get('phone', '').strip(),
                'address': request.POST.get('address', '').strip(),
                'city': request.POST.get('city', '').strip(),
                'state': request.POST.get('state', '').strip(),
                'zip_code': request.POST.get('zip_code', '').strip(),
                'country': request.POST.get('country', '').strip(),
            }
            
            payment_data = {
                'payment_method': request.POST.get('payment_method', ''),
                'card_name': request.POST.get('card_name', '').strip(),
                'card_number': request.POST.get('card_number', '').strip(),
            }
            
            special_instructions = request.POST.get('special_instructions', '').strip()
            
            # Basic validation
            required_shipping_fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'city', 'zip_code', 'country']
            missing_fields = [field for field in required_shipping_fields if not shipping_data.get(field)]
            
            if missing_fields:
                messages.error(request, f'Please fill in all required fields: {", ".join(missing_fields)}')
                return render(request, 'store/checkout.html', {
                    'page_title': 'Checkout - Jasem Shuman Art',
                    'cart_items': cart_items,
                    'cart': cart,
                    'form_data': request.POST,
                    'shipping_cost': Decimal('25.00'),
                    'total_amount': cart.total_price + Decimal('25.00'),
                })
            
            # Validate payment method
            if payment_data['payment_method'] not in ['credit_card', 'paypal']:
                messages.error(request, 'Please select a valid payment method.')
                return render(request, 'store/checkout.html', {
                    'page_title': 'Checkout - Jasem Shuman Art',
                    'cart_items': cart_items,
                    'cart': cart,
                    'form_data': request.POST,
                })
            
            # Calculate totals
            subtotal = cart.total_price
            shipping_cost = Decimal('25.00')  # Fixed shipping for now
            total_amount = subtotal + shipping_cost
            
            # Create order
            order = Order.objects.create(
                customer=request.user,
                subtotal=subtotal,
                shipping_cost=shipping_cost,
                total_amount=total_amount,
                customer_notes=special_instructions,
                order_status='pending'
            )
            
            # Create order items from cart
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    artwork=cart_item.artwork,
                    item_type=cart_item.item_type,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.unit_price,
                    total_price=cart_item.total_price
                )
            
            # Create shipping address
            ShippingAddress.objects.create(
                order=order,
                full_name=f"{shipping_data['first_name']} {shipping_data['last_name']}",
                phone=shipping_data['phone'],
                email=shipping_data['email'],
                address_line_1=shipping_data['address'],
                city=shipping_data['city'],
                state=shipping_data['state'],  # Can be empty for countries that don't use states
                postal_code=shipping_data['zip_code'],
                country=shipping_data['country'],
                delivery_instructions=special_instructions
            )
            
            # Create payment info
            PaymentInfo.objects.create(
                order=order,
                payment_method=payment_data['payment_method'],
                cardholder_name=payment_data.get('card_name', ''),
                card_last_four=payment_data.get('card_number', '')[-4:] if payment_data.get('card_number') else '',
                transaction_reference=f"ORDER-{order.id}-{order.created_at.strftime('%Y%m%d')}"
            )
            
            # Clear the cart
            cart_items.delete()
            
            # Success message and redirect
            messages.success(request, f'Order #{order.id} placed successfully! You will receive a confirmation email shortly.')
            return redirect('store:order_success', order_id=order.id)
            
        except Exception as e:
            messages.error(request, 'An error occurred while processing your order. Please try again.')
            return render(request, 'store/checkout.html', {
                'page_title': 'Checkout - Jasem Shuman Art',
                'cart_items': cart_items,
                'cart': cart,
                'form_data': request.POST,
            })
    
    # GET request - display checkout form
    shipping_cost = Decimal('25.00')
    context = {
        'page_title': 'Checkout - Jasem Shuman Art',
        'cart_items': cart_items,
        'cart': cart,
        'shipping_cost': shipping_cost,
        'total_amount': cart.total_price + shipping_cost,
    }
    return render(request, 'store/checkout.html', context)


@login_required
def order_success(request, order_id):
    """Order success page"""
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    
    context = {
        'page_title': f'Order Confirmation - Jasem Shuman Art',
        'order': order,
    }
    return render(request, 'store/order_success.html', context)


@login_required
def order_history(request):
    """User order history"""
    # Get user's orders
    orders = Order.objects.filter(customer=request.user).select_related(
        'payment_info', 'shipping_address'
    ).prefetch_related('items__artwork').order_by('-created_at')
    
    context = {
        'page_title': 'Order History - Jasem Shuman Art',
        'orders': orders,
    }
    return render(request, 'store/order_history.html', context)


@login_required
def order_detail(request, order_id):
    """Individual order detail"""
    # Get order for current user only
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    
    # Ensure payment_info and shipping_address exist (add error handling)
    if not hasattr(order, 'payment_info'):
        messages.warning(request, 'Payment information is not available for this order.')
    
    if not hasattr(order, 'shipping_address'):
        messages.warning(request, 'Shipping address is not available for this order.')
    
    context = {
        'page_title': f'Order #{order_id} - Jasem Shuman Art',
        'order': order,
    }
    return render(request, 'store/order_detail.html', context)
