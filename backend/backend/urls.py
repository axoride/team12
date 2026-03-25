from django.contrib import admin
from django.urls import path, include
from api import views

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),

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
    path('api/cart/remove/', views.remove_from_cart),

    # -------------------
    # Wishlist Management
    # -------------------
    path('api/wishlists/create/', views.create_wishlist),
    path('api/wishlist/', views.add_book_to_wishlist),

    # -------------------
    # Book Browsing & Sorting
    # -------------------
    path('api/books/genre/', views.books_by_genre, name='books_by_genre'),
    path('api/books/top-sellers/', views.top_sellers, name='top_sellers'),
    path('api/books/rating/', views.books_by_rating, name='books_by_rating'),
    path('api/books/discount/', views.discount_books_by_publisher, name='discount_books_by_publisher'),

    # -------------------
    # Book Details
    # -------------------
    path('api/books/create/', views.create_book),
    path('api/books/<str:isbn>/', views.retrieve_book_by_isbn),

    # -------------------
    # Book Rating & Commenting
    # -------------------
    path('api/books/<str:isbn>/reviews/', views.get_book_reviews),
    path('api/books/<str:isbn>/ratings/', views.submit_rating),
    path('api/books/<str:isbn>/comments/', views.submit_comment),
]


