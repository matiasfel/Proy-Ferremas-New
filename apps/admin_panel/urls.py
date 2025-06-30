from django.urls import path
from . import views
from .views_api import ProductStockAPIView

app_name = "admin_panel"

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='dashboard'),
    
    #Orders URLs
    path('orders/',    views.admin_orders,    name='orders'),
    path('order/<str:order_id>/', views.admin_order_detail, name='admin_order_detail'),
    
    # Admin Products URLs
    path('products/',  views.admin_products,  name='products'),
    path('products/create/',                  views.product_create, name='product_create'),
    path('products/<int:product_id>/edit/',   views.product_edit,   name='product_edit'),
    path('products/<int:product_id>/delete/', views.product_delete, name='product_delete'),
    
    # Admin categories URLs
    path('categories/', views.admin_categories, name='categories'),
    path('category/create/', views.admin_category_create, name='admin_category_create'),
    path('category/edit/<int:category_id>/', views.admin_category_edit, name='admin_category_edit'),
    path('category/delete/<int:category_id>/', views.admin_category_delete, name='admin_category_delete'),
    
    #brands URLs
    path('brands/',    views.admin_brands,    name='brands'),
    path('brand/create/',  views.admin_brand_create, name='admin_brand_create'),
    path('brand/edit/<int:brand_id>/', views.admin_brand_edit, name='admin_brand_edit'),
    path('brand/delete/<int:brand_id>/', views.admin_brand_delete, name='admin_brand_delete'),
    
    # users
    path('users/',     views.admin_users,     name='users'),
    path('users/create/', views.admin_user_create, name='admin_user_create'),
    path('users/<int:user_id>/edit/', views.admin_user_edit, name='admin_user_edit'),
    path('users/<int:user_id>/delete/', views.admin_user_delete, name='admin_user_delete'),
    
    #Messages
    path('messages/',  views.admin_messages,  name='messages'),
    path('message/<int:message_id>/delete/', views.admin_message_delete, name='admin_message_delete'),
    
    #Serializer/apiview
    path('restframework/', views.admin_restframework, name='restframework'),
    path('api_products/', ProductStockAPIView.as_view(), name='api_products'),
    
    #config
    path('config/',    views.admin_config,    name='config'),
]