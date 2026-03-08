from django.contrib import admin
from django.urls import path
from api import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Create User
    path('api/users/', views.create_user),

    # Retrieve User by Username
    path('api/users/<str:username>/', views.get_user),
]