from django.shortcuts import render, redirect, get_object_or_404
from apps.store.models.orders import Order
from apps.store.models.product import Product
from apps.users.models import CustomUser
from django.db.models import Sum
from .forms import ProductForm
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from decimal import Decimal
from apps.store.models import Category, Brand
from .forms import CategoryForm, BrandForm, UserForm, UserCreateForm
from apps.landing.models import ContactMessage

def is_admin(user):
    return user.is_authenticated and user.is_staff

User = CustomUser  # Modelo usuario personalizado

@user_passes_test(is_admin)
def admin_dashboard(request):
    """
    Render the admin dashboard page con los últimos pedidos reales.
    """
    total_pedidos = Order.objects.count()
    total_usuarios = CustomUser.objects.filter(is_superuser=False).count()
    total_ventas = Order.objects.filter(status=Order.STATUS_PAID).aggregate(total=Sum('total'))['total'] or 0
    latest_orders = Order.objects.select_related('user').order_by('-created_at')[:5]

    context = {
        'total_pedidos': total_pedidos,
        'total_usuarios': total_usuarios,
        'total_ventas': total_ventas,
        'latest_orders': latest_orders,
    }
    return render(request, 'admin_panel/dashboard.html', context)

# Orders views
@user_passes_test(is_admin)
def admin_orders(request):
    query = request.GET.get('q', '')
    status = request.GET.get('status', '')
    
    orders = Order.objects.all().select_related('user')
    
    if query:
        orders = orders.filter(Q(user__username__icontains=query) | Q(id__icontains=query))
    if status:
        orders = orders.filter(status=status)

    return render(request, 'admin_panel/orders.html', {'orders': orders})

@user_passes_test(is_admin)
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    items = order.items.all()

    subtotal = sum((item.subtotal for item in items), Decimal('0.00'))

    # Construir dirección completa (si es que la quieres mostrar junta)
    if order.shipping_address:
        shipping_address = f"{order.shipping_address}, {order.shipping_city}, {order.shipping_region}, {order.shipping_zip}"
    else:
        shipping_address = None

    context = {
        'order': order,
        'items': items,
        'subtotal': subtotal,
        'shipping_address': shipping_address,
    }
    return render(request, 'admin_panel/order_detail.html', context)

# admin products views
@user_passes_test(is_admin)
def admin_products(request):
    q = request.GET.get('q', '')
    products_list = Product.objects.all()

    if q:
        products_list = products_list.filter(
            Q(name__icontains=q) |
            Q(brand__name__icontains=q) |
            Q(category__name__icontains=q)
        )

    # Verifica que el queryset no esté vacío
    if products_list.exists():
        try:
            products_list = products_list.order_by('-created_at')
        except Exception as e:
            print(f"Error en order_by: {e}")
            # Ordena por id si created_at falla
            products_list = products_list.order_by('-id')
    else:
        products_list = products_list.order_by('-id')

    paginator = Paginator(products_list, 10)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    context = {
        'products': products,
    }
    return render(request, 'admin_panel/products.html', context)

@user_passes_test(is_admin)
def product_create(request):
    """
    Crear un nuevo producto.
    """
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)  # OJO: request.FILES para imagen
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto agregado correctamente')
            return redirect('admin_panel:products')
    else:
        form = ProductForm()
    return render(request, 'admin_panel/product_create.html', {'form': form})

@user_passes_test(is_admin)
def product_edit(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado correctamente.')
            return redirect('admin_panel:products')
    else:
        form = ProductForm(instance=product)
    return render(request, 'admin_panel/product_edit.html', {'form': form, 'product': product})

@user_passes_test(is_admin)
def product_delete(request, product_id):
    print(f"Attempting to delete product with ID: {product_id}")
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Producto eliminado correctamente')
        return redirect('admin_panel:products')
    # Ya no necesitas mostrar una página de confirmación, porque ahora usas modal
    return redirect('admin_panel:products')

@user_passes_test(is_admin)
def admin_categories(request):
    """
    Renderiza la lista de categorías con búsqueda y paginación.
    """
    query = request.GET.get('q', '')
    categories = Category.objects.all()

    if query:
        categories = categories.filter(name__icontains=query)

    paginator = Paginator(categories, 10)  # 10 por página
    page = request.GET.get('page')
    categories_paginated = paginator.get_page(page)

    return render(request, 'admin_panel/categories.html', {
        'categories': categories_paginated,
        'query': query
    })

@user_passes_test(is_admin)
def admin_category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría creada exitosamente.')
            return redirect('admin_panel:categories')
    else:
        form = CategoryForm()

    return render(request, 'admin_panel/category_create.html', {'form': form})

@user_passes_test(is_admin)
def admin_category_edit(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría actualizada correctamente.')
            return redirect('admin_panel:categories')
    else:
        form = CategoryForm(instance=category)

    return render(request, 'admin_panel/category_edit.html', {
        'form': form,
        'category': category
    })

@user_passes_test(is_admin)
def admin_category_delete(request, category_id):
    """
    Delete an existing category.
    """
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Categoría eliminada correctamente')
        return redirect('admin_panel:categories')
    
    messages.error(request, 'Acción no permitida')
    return redirect('admin_panel:categories')

# brands view:
@user_passes_test(is_admin)
def admin_brands(request):
    query = request.GET.get('q', '')
    brands = Brand.objects.all()
    if query:
        brands = brands.filter(name__icontains=query)
    # Paginación (opcional)
    from django.core.paginator import Paginator
    paginator = Paginator(brands.order_by('name'), 10)
    page_number = request.GET.get('page')
    brands_page = paginator.get_page(page_number)
    
    context = {
        'brands': brands_page,
    }
    return render(request, 'admin_panel/brands.html', context)

@user_passes_test(is_admin)
def admin_brand_create(request):
    if request.method == 'POST':
        form = BrandForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Marca creada correctamente')
            return redirect('admin_panel:brands')
    else:
        form = BrandForm()
    return render(request, 'admin_panel/brand_create.html', {'form': form})

@user_passes_test(is_admin)
def admin_brand_edit(request, brand_id):
    brand = get_object_or_404(Brand, pk=brand_id)
    if request.method == 'POST':
        form = BrandForm(request.POST, instance=brand)
        if form.is_valid():
            form.save()
            messages.success(request, 'Marca actualizada correctamente')
            return redirect('admin_panel:brands')
    else:
        form = BrandForm(instance=brand)
    return render(request, 'admin_panel/brand_edit.html', {'form': form})

@user_passes_test(is_admin)
def admin_brand_delete(request, brand_id):
    brand = get_object_or_404(Brand, pk=brand_id)
    if request.method == 'POST':
        brand.delete()
        messages.success(request, 'Marca eliminada correctamente')
        return redirect('admin_panel:brands')
    # Si se accede con GET, redirige o muestra error según prefieras
    return redirect('admin_panel:brands')

# Users views
@user_passes_test(is_admin)
def admin_users(request):
    query = request.GET.get('q', '')
    users = CustomUser.objects.all()

    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(role__icontains=query)
        )

    paginator = Paginator(users.order_by('id'), 10)  # paginar si es necesario
    page_number = request.GET.get('page')
    users_page = paginator.get_page(page_number)

    return render(request, 'admin_panel/users.html', {
        'users': users_page,
    })

@user_passes_test(is_admin)
def admin_user_create(request):
    """
    Crear un nuevo usuario.
    """
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Importante
            user.save()
            messages.success(request, 'Usuario creado correctamente.')
            return redirect('admin_panel:users')
    else:
        form = UserCreateForm()

    return render(request, 'admin_panel/user_create.html', {'form': form})

@user_passes_test(is_admin)
def admin_user_edit(request, user_id):
    """
    Editar un usuario existente.
    """
    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario actualizado correctamente.')
            return redirect('admin_panel:users')
    else:
        form = UserForm(instance=user)

    return render(request, 'admin_panel/user_edit.html', {'form': form, 'user': user})

@user_passes_test(is_admin)
def admin_user_delete(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Usuario eliminado correctamente')
        return redirect('admin_panel:users')
    return redirect('admin_panel:users')

# Messages view:
@user_passes_test(is_admin)
def admin_messages(request):
    """
    Visualiza todos los mensajes de contacto.
    """
    messages_list = ContactMessage.objects.order_by('-date')
    return render(request, 'admin_panel/messages.html', {
        'messages_list': messages_list,
    })

@user_passes_test(is_admin)
def admin_message_delete(request, message_id):
    message = get_object_or_404(ContactMessage, id=message_id)
    message.delete()
    messages.success(request, 'Mensaje eliminado correctamente.')
    return redirect('admin_panel:messages')

# Config view:
@user_passes_test(is_admin)
def admin_config(request):
    """
    Render the admin settings page.
    """
    return render(request, 'admin_panel/config.html')