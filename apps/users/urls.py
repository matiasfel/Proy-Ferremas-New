from django.urls import path
from . import views

app_name = 'apps.users'

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('orders/', views.orders_history, name='orders_history'),
]