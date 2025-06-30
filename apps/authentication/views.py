from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.contrib.auth import get_user_model

User = get_user_model()

def login(request):
    # Comprobar si el usuario ya ha iniciado sesión
    if request.user.is_authenticated:
        messages.info(request, 'Ya has iniciado sesión.')
        return redirect('landing:index')  # Redirigir a la página principal o dashboard

    # Mostrar mensaje si fue redirigido desde una vista protegida
    if 'next' in request.GET:
        messages.warning(request, 'Debes iniciar sesión para agregar productos al carrito.')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Validación de campos vacíos
        if not username or not password:
            messages.warning(request, 'Todos los campos son obligatorios.')
            return render(request, 'authentication/login.html')

        # Limitar intentos de inicio de sesión
        if request.session.get('login_attempts', 0) >= 5:
            messages.warning(request, 'Demasiados intentos fallidos. Intenta nuevamente más tarde.')
            return render(request, 'authentication/login.html')

        # Autenticación
        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            request.session['login_attempts'] = 0  # Reiniciar contador

            # Redirigir al next si existe
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)

            return redirect('landing:index')  # Redirección por defecto

        else:
            messages.warning(request, 'Nombre de usuario o contraseña incorrectos.')
            request.session['login_attempts'] = request.session.get('login_attempts', 0) + 1

    return render(request, 'authentication/login.html')

def register(request):
    if request.user.is_authenticated:
        messages.info(request, 'Ya has iniciado sesión.')
        return redirect('landing:index')
    
    if request.method == 'POST':
        username = request.POST.get('username').strip()
        email = request.POST.get('email').strip()
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if not username or not email or not password or not password2:
            messages.warning(request, 'Todos los campos son obligatorios.')
            return render(request, 'authentication/register.html')

        if password != password2:
            messages.warning(request, 'Las contraseñas no coinciden.')
            return render(request, 'authentication/register.html')

        User = get_user_model()  # ← esta línea es clave

        if User.objects.filter(username=username).exists():
            messages.warning(request, 'El nombre de usuario ya está en uso.')
            return render(request, 'authentication/register.html')

        if User.objects.filter(email=email).exists():
            messages.warning(request, 'El correo electrónico ya está registrado.')
            return render(request, 'authentication/register.html')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        messages.success(request, 'Cuenta creada correctamente. Ya puedes iniciar sesión.')
        return redirect('authentication:login')

    return render(request, 'authentication/register.html')

def logout(request):
    from django.contrib.auth import logout as auth_logout
    auth_logout(request)
    messages.success(request, 'Has cerrado sesión correctamente.')
    return redirect('authentication:login')  # o tu página principal
