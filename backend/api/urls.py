from django.urls import path
from . import views

urlpatterns = [
    path('books/genre/', views.books_by_genre),
    path('books/top-sellers/', views.top_sellers),
    path('books/rating/', views.books_by_rating),
    path('books/discount/', views.discount_books_by_publisher),
]
