from django.urls import path
from . import views

urlpatterns = [
    path('books/genre/', views.books_by_genre),
]
