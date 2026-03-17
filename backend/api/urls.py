from django.urls import path
from . import views

urlpatterns = [
    # -------------------
    # Book Browsing & Sorting
    # -------------------
    path('books/genre/', views.books_by_genre),
    path('books/top-sellers/', views.top_sellers),
    path('books/rating/', views.books_by_rating),
    path('books/discount/', views.discount_books_by_publisher),
    
    # -------------------
    # Profile Management
    # -------------------
    path('users/create/', views.create_user),
    path('users/<str:username>/', views.get_user),

    # -------------------
    # Shopping Cart
    # -------------------
    path('cart/', views.get_cart_items),
    path('cart/add/', views.add_to_cart),
    path('cart/subtotal/', views.get_cart_subtotal),

    # -------------------
    # Book Details
    # -------------------
    path('books/create/', views.create_book),
    path('books/<str:isbn>/', views.retrieve_book_by_isbn),

    # -------------------
    # Wishlist Management
    # -------------------
    path('wishlists/create/', views.create_wishlist),
    path('wishlists/add-book/', views.add_book_to_wishlist),

    # -------------------
    # Book Rating & Commenting
    # -------------------
    path('books/<str:isbn>/reviews/', views.get_book_reviews),
    path('books/<str:isbn>/ratings/', views.submit_rating),
    path('books/<str:isbn>/comments/', views.submit_comment),
]
