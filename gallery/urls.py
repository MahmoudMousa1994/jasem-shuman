from django.urls import path
from . import views

app_name = 'gallery'

urlpatterns = [
    path('', views.gallery_home, name='home'),
    path('artwork/<int:pk>/', views.artwork_detail, name='artwork_detail'),
    path('category/<str:category_name>/', views.category_view, name='category'),
    path('api/artworks/', views.artwork_api, name='artwork_api'),  # For AJAX filtering
]