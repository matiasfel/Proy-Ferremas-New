from django.db.models import Sum
from apps.store.models import Cart, CartItem

def cart_item_count(request):
    count = 0
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            count = CartItem.objects.filter(cart=cart).aggregate(total=Sum('quantity'))['total'] or 0
    return {'cart_item_count': count}