from django.contrib import admin
from django.urls import path
from api import views

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # -------------------
    # Profile Management
    # -------------------
    path('api/users/', views.create_user),              # POST - Create User
    path('api/users/<str:username>/', views.get_user),  # GET - Retrieve User by username

    # -------------------
    # Shopping Cart
    # -------------------
    path('api/cart/', views.get_cart_items),            # GET - Retrieve all cart items
    path('api/cart/add/', views.add_to_cart),           # POST - Add item to cart
    path('api/cart/subtotal/', views.get_cart_subtotal),# GET - Cart subtotal by user_id

    # -------------------
    # Wishlist Management
    # -------------------
    path('api/wishlists/create/', views.create_wishlist),  # POST - Create wishlist
    path('api/wishlist/', views.add_book_to_wishlist),     # POST - Add book to wishlist

    # -------------------
    # Book Details
    # -------------------
    path('api/books/create/', views.CreateBookView.as_view()),    # POST - Create book
    path('api/books/<str:isbn>/', views.RetrieveBookByISBNView.as_view()), # GET - Book by ISBN

    # -------------------
    # Book Browsing & Sorting
    # -------------------
    path('api/books/genre/', views.books_by_genre, name='books_by_genre'),
    path('api/books/top-sellers/', views.top_sellers, name='top_sellers'),
]