from django.contrib import admin
from django.urls import path
from api import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/cart/', views.get_cart_items),
    path('api/cart/add/', views.add_to_cart),
    path('api/cart/subtotal/', views.get_cart_subtotal),
]