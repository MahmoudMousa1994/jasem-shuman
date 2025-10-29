from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.store_home, name='home'),
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/', views.update_cart_item, name='update_cart'),
    path('remove-from-cart/', views.remove_cart_item, name='remove_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.order_history, name='order_history'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('debug-cart/', views.debug_cart, name='debug_cart'),
    path('get-cart-count/', views.get_cart_count, name='get_cart_count'),
]