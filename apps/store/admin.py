from django.contrib import admin
from .models import Product, Brand, Category, Cart, CartItem, Order, OrderItem

""" Products """
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'price', 'stock', 'category', 'brand', 'is_active', 'is_featured']
    list_filter = ['category', 'brand', 'is_active', 'is_featured']
    search_fields = ['name', 'sku']
    
""" Cart """
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'get_total_price')

    def get_total_price(self, obj):
        return f"${obj.get_total_price():,.0f}"
    get_total_price.short_description = 'Total Price'

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at')
    list_filter = ('created_at',)
    inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'get_total_price')
    list_filter = ('product',)

    def get_total_price(self, obj):
        return f"${obj.get_total_price():,.0f}"
    get_total_price.short_description = 'Total Price'
    
""" Orders """

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('sku', 'product_name', 'quantity', 'price', 'subtotal')

    def subtotal(self, obj):
        return obj.subtotal

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'status', 'total', 'created_at',
        'shipping_city', 'shipping_region', 'payment_token'
    )
    list_filter = ('status', 'created_at', 'shipping_region')
    search_fields = ('user__username', 'shipping_address', 'payment_token', 'id')
    readonly_fields = ('created_at',)
    inlines = [OrderItemInline]

    fieldsets = (
        ("Información del pedido", {
            'fields': ('user', 'status', 'total', 'payment_token', 'created_at')
        }),
        ("Datos de envío", {
            'fields': (
                'shipping_address',
                'shipping_city',
                'shipping_region',
                'shipping_zip',
            )
        }),
        ("Notas adicionales", {
            'fields': ('notes',),
        }),
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product_name', 'sku', 'quantity', 'price', 'subtotal')
    search_fields = ('product_name', 'sku', 'order__id')
    readonly_fields = ('subtotal',)

    def subtotal(self, obj):
        return obj.subtotal