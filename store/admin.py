from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Order, OrderItem, ShippingAddress, PaymentInfo, Cart, CartItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price']
    fields = ['artwork', 'item_type', 'quantity', 'unit_price', 'total_price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'order_status', 'total_amount', 
                   'created_at', 'payment_status', 'shipping_country']
    list_filter = ['order_status', 'created_at', 'payment_info__is_paid', 'shipping_address__country']
    search_fields = ['customer__username', 'customer__email', 
                    'shipping_address__full_name', 'id']
    readonly_fields = ['total_amount', 'created_at', 'updated_at']
    
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('customer', 'order_status', 'created_at', 'updated_at')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'shipping_cost', 'total_amount')
        }),
        ('Notes', {
            'fields': ('customer_notes', 'admin_notes')
        }),
    )
    
    actions = ['mark_as_confirmed', 'mark_as_processing', 'mark_as_shipped', 'mark_as_delivered']
    
    def customer_name(self, obj):
        return obj.customer.get_full_name() or obj.customer.username
    customer_name.short_description = 'Customer'
    
    def shipping_country(self, obj):
        if hasattr(obj, 'shipping_address'):
            return obj.shipping_address.country
        return "No address"
    shipping_country.short_description = 'Ship To'
    
    def payment_status(self, obj):
        if hasattr(obj, 'payment_info'):
            is_paid = obj.payment_info.is_paid
            status_text = "Paid" if is_paid else "Pending"
            color = '#28a745' if is_paid else '#ffc107'
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span>',
                color, status_text
            )
        return "No payment info"
    payment_status.short_description = 'Payment Status'
    
    def mark_as_confirmed(self, request, queryset):
        queryset.update(order_status='confirmed')
        self.message_user(request, f'{queryset.count()} orders marked as confirmed.')
    mark_as_confirmed.short_description = 'Mark as Confirmed'
    
    def mark_as_processing(self, request, queryset):
        queryset.update(order_status='processing')
        self.message_user(request, f'{queryset.count()} orders marked as processing.')
    mark_as_processing.short_description = 'Mark as Processing'
    
    def mark_as_shipped(self, request, queryset):
        queryset.update(order_status='shipped')
        self.message_user(request, f'{queryset.count()} orders marked as shipped.')
    mark_as_shipped.short_description = 'Mark as Shipped'
    
    def mark_as_delivered(self, request, queryset):
        queryset.update(order_status='delivered')
        self.message_user(request, f'{queryset.count()} orders marked as delivered.')
    mark_as_delivered.short_description = 'Mark as Delivered'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('customer', 'payment_info', 'shipping_address')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order_link', 'artwork', 'item_type', 'quantity', 'unit_price', 'total_price']
    list_filter = ['item_type', 'order__order_status', 'order__created_at']
    search_fields = ['artwork__title', 'order__id']
    readonly_fields = ['total_price']
    
    def order_link(self, obj):
        url = reverse('admin:store_order_change', args=[obj.order.pk])
        return format_html('<a href="{}">Order #{}</a>', url, obj.order.id)
    order_link.short_description = 'Order'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order', 'artwork')


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'city', 'state', 'country', 'postal_code', 'order_id']
    list_filter = ['country', 'state']
    search_fields = ['full_name', 'city', 'email']
    
    def order_id(self, obj):
        return f"Order #{obj.order.id}"
    order_id.short_description = 'Order'


@admin.register(PaymentInfo)
class PaymentInfoAdmin(admin.ModelAdmin):
    list_display = ['order_link', 'payment_method', 'is_paid', 'payment_date']
    list_filter = ['payment_method', 'is_paid', 'payment_date']
    search_fields = ['order__id', 'transaction_reference']
    readonly_fields = ['payment_date']
    
    def order_link(self, obj):
        url = reverse('admin:store_order_change', args=[obj.order.pk])
        return format_html('<a href="{}">Order #{}</a>', url, obj.order.id)
    order_link.short_description = 'Order'
    
    actions = ['mark_as_paid']
    
    def mark_as_paid(self, request, queryset):
        for payment in queryset:
            payment.mark_as_paid()
        self.message_user(request, f'{queryset.count()} payments marked as paid.')
    mark_as_paid.short_description = 'Mark selected payments as paid'


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['total_price']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['cart_owner', 'items_count', 'total_price', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'user__email', 'session_key']
    readonly_fields = ['total_price', 'total_items', 'created_at', 'updated_at']
    
    inlines = [CartItemInline]
    
    def cart_owner(self, obj):
        if obj.user:
            return obj.user.username
        return f"Anonymous ({obj.session_key})"
    cart_owner.short_description = 'Owner'
    
    def items_count(self, obj):
        return obj.total_items
    items_count.short_description = 'Items'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart_owner', 'artwork', 'item_type', 'quantity', 'total_price']
    list_filter = ['item_type', 'cart__created_at']
    search_fields = ['cart__user__username', 'artwork__title']
    readonly_fields = ['total_price', 'unit_price']
    
    def cart_owner(self, obj):
        if obj.cart.user:
            return obj.cart.user.username
        return f"Anonymous ({obj.cart.session_key})"
    cart_owner.short_description = 'Cart Owner'
