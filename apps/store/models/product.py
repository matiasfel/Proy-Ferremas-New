from django.db import models

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Nombre de la marca

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Nombre de la categoría (ej: Herramientas, Pintura)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)  # Nombre del producto
    sku = models.CharField(max_length=50, unique=True)  # Código único interno SKU
    description = models.TextField(blank=True)  # Descripción opcional
    image = models.ImageField(upload_to='products/')  # Imagen del producto
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Precio con dos decimales
    stock = models.PositiveIntegerField()  # Stock disponible, solo números positivos
    unit = models.CharField(max_length=20, default='unit')  # Unidad de medida, ej: 'unit', 'kg', 'liter'
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)  # Categoría, opcional
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)  # Marca, opcional
    is_featured = models.BooleanField(default=False)  # Producto destacado para promociones
    is_active = models.BooleanField(default=True)  # Activo o desactivado en el catálogo
    created_at = models.DateTimeField(auto_now_add=True)  # Fecha de creación automática

    def __str__(self):
        return f"{self.name} ({self.sku})"