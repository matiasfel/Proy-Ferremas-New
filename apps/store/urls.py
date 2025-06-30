from django.urls import path
from . import views

app_name = "store"

urlpatterns = [
    # Product related URLs
    path("products/", views.products, name="products"),
    path("products/<int:pk>/", views.product_detail, name="product_detail"),
    
    # Cart-related URLs
    path("cart/", views.cart, name="cart"),
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/update/<int:item_id>/", views.update_cart_item, name="update_cart_item"),
    path("cart/remove/<int:item_id>/", views.remove_cart_item, name="remove_cart_item"),
    
    # Payment URLs
    path('payment/start/', views.start_payment, name='start_payment'),
    path('payment/commit/', views.commit_payment, name='commit_payment'),
    
    # order-related URLs
    path('orders/<int:pk>/', views.order_detail, name='detail'),

]