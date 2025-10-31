from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta
from store.models import Order, OrderItem
from gallery.models import Artwork

@staff_member_required
def admin_dashboard(request):
    """Admin dashboard with order statistics"""
    
    # Date ranges
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Order statistics
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(order_status='pending').count()
    processing_orders = Order.objects.filter(order_status='processing').count()
    shipped_orders = Order.objects.filter(order_status='shipped').count()
    
    # Recent orders
    recent_orders = Order.objects.select_related('customer', 'payment_info').order_by('-created_at')[:10]
    
    # Revenue statistics
    total_revenue = Order.objects.filter(
        payment_info__is_paid=True
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    weekly_revenue = Order.objects.filter(
        created_at__gte=week_ago,
        payment_info__is_paid=True
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # Popular artworks
    popular_artworks = OrderItem.objects.values('artwork__title').annotate(
        total_sold=Count('id')
    ).order_by('-total_sold')[:5]
    
    # Countries ordering from
    top_countries = Order.objects.select_related('shipping_address').exclude(
        shipping_address__country=''
    ).values('shipping_address__country').annotate(
        order_count=Count('id')
    ).order_by('-order_count')[:10]
    
    context = {
        'page_title': 'Admin Dashboard - Jasem Shuman Art',
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'processing_orders': processing_orders,
        'shipped_orders': shipped_orders,
        'recent_orders': recent_orders,
        'total_revenue': total_revenue,
        'weekly_revenue': weekly_revenue,
        'popular_artworks': popular_artworks,
        'top_countries': top_countries,
    }
    
    return render(request, 'admin/dashboard.html', context)