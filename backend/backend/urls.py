from django.contrib import admin
from django.urls import path
from api import views

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # -------------------
    # Profile Management
    # -------------------
    path('api/users/', views.create_user),
    path('api/users/<str:username>/', views.get_user),

    # -------------------
    # Shopping Cart
    # -------------------
    path('api/cart/', views.get_cart_items),
    path('api/cart/add/', views.add_to_cart),
    path('api/cart/subtotal/', views.get_cart_subtotal),

    # -------------------
    # Wishlist Management
    # -------------------
    path('api/wishlists/create/', views.create_wishlist),
    path('api/wishlist/', views.add_book_to_wishlist),

    # -------------------
    # Book Browsing & Sorting  ← MOVED ABOVE the dynamic <isbn> route
    # -------------------
    path('api/books/genre/', views.books_by_genre, name='books_by_genre'),
    path('api/books/top-sellers/', views.top_sellers, name='top_sellers'),

    # -------------------
    # Book Details        ← Dynamic route LAST among /api/books/ paths
    # -------------------
    path('api/books/create/', views.create_book),
    path('api/books/<str:isbn>/', views.retrieve_book_by_isbn),
]