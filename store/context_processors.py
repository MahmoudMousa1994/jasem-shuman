from .models import Cart


def cart_context(request):
    """Add cart information to all templates"""
    cart_count = 0
    
    try:
        if request.user.is_authenticated:
            # For authenticated users, get cart by user
            try:
                cart = Cart.objects.get(user=request.user)
                cart_count = cart.total_items
            except Cart.DoesNotExist:
                cart_count = 0
        else:
            # For anonymous users, check session-based cart
            if hasattr(request, 'session'):
                # Only look for existing session, don't create new one here
                # to avoid session creation on every request
                if request.session.session_key:
                    try:
                        cart = Cart.objects.get(session_key=request.session.session_key)
                        cart_count = cart.total_items
                    except Cart.DoesNotExist:
                        cart_count = 0
                else:
                    # No session key means no cart yet
                    cart_count = 0
    except Exception as e:
        # Fallback to 0 if anything goes wrong
        cart_count = 0
    
    return {
        'cart_count': cart_count
    }