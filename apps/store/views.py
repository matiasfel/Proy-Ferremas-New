from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from apps.store.models import Product, Cart, CartItem, OrderItem
from .models import Order

from transbank.webpay.webpay_plus.transaction import Transaction, WebpayOptions
from transbank.common.integration_type import IntegrationType
from transbank.error.transbank_error import TransbankError
from django.views.decorators.csrf import csrf_exempt

from django.core.paginator import Paginator

def products(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    page_number = request.GET.get('page')

    products_list = Product.objects.all()

    if query:
        products_list = products_list.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )

    if category:
        products_list = products_list.filter(category__name__iexact=category)

    paginator = Paginator(products_list, 12)  # 12 productos por página
    products = paginator.get_page(page_number)

    categories = Product.objects.values_list('category__name', flat=True).distinct()

    return render(request, 'store/products.html', {
        'products': products,
        'query': query,
        'category': category,
        'categories': categories,
    })

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'store/product_detail.html', {'product': product})

# Carrito

def cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        items = CartItem.objects.filter(cart=cart)
    else:
        items = []

    # Subtotal
    subtotal = sum(item.get_total_price() for item in items)

    # Impuesto (IVA 19%)
    tax = subtotal * Decimal('0.19')

    # Envío: gratis si subtotal >= 50000
    shipping = Decimal('0.00') if subtotal >= 50000 else Decimal('3990')

    # Total final
    total = subtotal + tax + shipping

    # Verificar si hay algún producto con stock insuficiente
    stock_issue = any(item.product.stock < item.quantity for item in items)

    context = {
        'items': items,
        'subtotal': subtotal,
        'tax': tax,
        'shipping': shipping,
        'total': total,
        'stock_issue': stock_issue,
    }
    return render(request, 'store/cart.html', context)

# Agregar producto al carrito
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        # Si usas carrito en sesión:
        messages.error(request, "Debes iniciar sesión para agregar al carrito.")
        return redirect('authentication:login')

    # Obtener o crear item existente
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    # Total deseado = lo que ya hay en carrito + lo que quiere agregar
    total_quantity = cart_item.quantity + quantity if not created else quantity

    if total_quantity > product.stock:
        messages.error(request, f"Has llegado al limite de stock disponible. Stock actual: {product.stock}.")
        return redirect('store:product_detail', pk=product.id)

    # Actualizar cantidad
    cart_item.quantity = total_quantity
    cart_item.save()

    messages.success(request, "Producto agregado al carrito.", extra_tags="added")
    return redirect('store:cart')

# Actualizar cantidad de un item del carrito
@login_required
def update_cart_item(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(CartItem, id=item_id)

        try:
            new_quantity = int(request.POST.get('quantity'))
        except (TypeError, ValueError):
            messages.error(request, "Cantidad inválida.")
            return redirect('store:cart')

        if new_quantity < 1:
            messages.error(request, "La cantidad debe ser al menos 1.")
            return redirect('store:cart')

        if new_quantity > item.product.stock:
            messages.error(request, f"No hay suficiente stock disponible. Stock actual: {item.product.stock}.")
            return redirect('store:cart')

        item.quantity = new_quantity
        item.save()
        messages.success(request, "Cantidad actualizada correctamente.")

    return redirect('store:cart')

# Eliminar un item del carrito
@login_required
def remove_cart_item(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        cart_item.delete()

    return redirect('store:cart')

#Webpay

@login_required
def start_payment(request):
    cart = get_object_or_404(Cart, user=request.user)
    items = CartItem.objects.filter(cart=cart)

    subtotal = sum(item.get_total_price() for item in items)
    tax = subtotal * Decimal('0.19')
    shipping = Decimal('0.00') if subtotal >= 50000 else Decimal('3990')
    total = subtotal + tax + shipping

    buy_order = f"ORDER{cart.id}"
    session_id = f"SESSION{request.user.id}"
    return_url = request.build_absolute_uri('/store/payment/commit/')

    options = WebpayOptions(
        commerce_code='597055555532',
        api_key='579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C',
        integration_type=IntegrationType.TEST
    )

    transaction = Transaction(options)
    # Convierte total a entero para evitar error
    response = transaction.create(buy_order, session_id, str(int(total)), return_url)

    return redirect(response['url'] + '?token_ws=' + response['token'])

@csrf_exempt
def commit_payment(request):
    token = request.GET.get('token_ws')
    canceled_token = request.GET.get('TBK_TOKEN')

    if not token and canceled_token:
        messages.warning(request, "El pago fue cancelado por el usuario.")
        return render(request, 'store/payment_cancelled.html')

    if not token:
        messages.error(request, "Token de pago no válido.")
        return redirect('store:cart')

    # ✅ Si ya existe una orden con ese token, redirigir al detalle
    existing_order = Order.objects.filter(payment_token=token).first()
    if existing_order:
        messages.info(request, "Este pago ya fue procesado.")
        return redirect('store:detail', pk=existing_order.pk)

    options = WebpayOptions(
        commerce_code='597055555532',
        api_key='579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C',
        integration_type=IntegrationType.TEST
    )
    transaction = Transaction(options)

    try:
        response = transaction.commit(token)

        if response['status'] != 'AUTHORIZED':
            messages.error(request, "El pago no fue autorizado.")
            return render(request, 'store/payment_error.html')

        cart = get_object_or_404(Cart, user=request.user)
        items = CartItem.objects.filter(cart=cart)

        if not items.exists():
            messages.error(request, "No se encontraron productos en el carrito.")
            return redirect('store:cart')

        subtotal = sum(item.get_total_price() for item in items)
        tax = subtotal * Decimal('0.19')

        if subtotal >= 50000:
            shipping = Decimal('0.00')
            discount = Decimal('3990')
        else:
            shipping = Decimal('3990')
            discount = Decimal('0.00')

        total = subtotal + tax + shipping - discount

        # ✅ Crear la orden asociando el token
        order = Order.objects.create(
            user=request.user,
            status=Order.STATUS_PAID,
            total=total,
            payment_token=token
        )

        for item in items:
            OrderItem.objects.create(
                order=order,
                sku=item.product.sku,
                product_name=item.product.name,
                quantity=item.quantity,
                price=item.product.price
            )

            product = item.product
            if product.stock >= item.quantity:
                product.stock -= item.quantity
                product.save()
            else:
                messages.error(request, f"No hay stock suficiente para {product.name}.")
                return render(request, 'store/payment_error.html')

        items.delete()

        messages.success(request, "¡Pago realizado con éxito!")
        return render(request, 'store/payment_success.html', {
            'response': response,
            'order': order,
            'subtotal': subtotal,
            'tax': tax,
            'shipping': shipping,
            'discount': discount,
        })

    except TransbankError as e:
        messages.error(request, f"Error al confirmar el pago: {str(e)}")
        return render(request, 'store/payment_error.html')

@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    items = order.items.all()

    subtotal = sum(item.subtotal for item in items)
    tax = subtotal * Decimal('0.19')

    discount = Decimal('0.00')
    shipping = Decimal('3990')  # envío por defecto

    if subtotal >= Decimal('50000'):
        discount = Decimal('3990')  # descuento equivalente al envío
        shipping = Decimal('0.00')

    total = subtotal + tax + shipping - discount

    context = {
        'order': order,
        'items': items,
        'subtotal': subtotal,
        'tax': tax,
        'shipping': shipping,
        'discount': discount,
        'total': total,
    }
    return render(request, 'store/order_detail.html', context)