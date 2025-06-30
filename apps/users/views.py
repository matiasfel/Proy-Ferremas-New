from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from apps.store.models import Order

@login_required
def profile(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-created_at')

    context = {
        'user': user,
        'orders': orders,
    }
    return render(request, 'users/profile.html', context)

@login_required
def edit_profile(request):
    user = request.user

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', '').strip()
        user.last_name = request.POST.get('last_name', '').strip()
        user.email = request.POST.get('email', '').strip()
        user.phone = request.POST.get('phone', '').strip()
        user.address = request.POST.get('address', '').strip()
        
        user.save()
        messages.success(request, 'Tu perfil ha sido actualizado correctamente.')
        return redirect('users:profile')

    return render(request, 'users/edit_profile.html', {'user': user})

@login_required
def orders_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'users/orders_history.html', {'orders': orders})