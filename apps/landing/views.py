from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ContactMessage

def index(request):
    return render(request, 'landing/index.html')

def about(request):
    return render(request, 'landing/about.html')

def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        if not (name and email and message):
            messages.error(request, "Por favor, completa todos los campos.")
            return render(request, "landing/contact.html")

        # Verificar si ya existe un mensaje con ese email
        if ContactMessage.objects.filter(email=email).exists():
            messages.error(request, "Ya has enviado un mensaje previamente. ¡Gracias!")
            return render(request, "landing/contact.html")

        # Si no existe, guardar el mensaje
        ContactMessage.objects.create(name=name, email=email, message=message)
        messages.success(request, "¡Mensaje enviado correctamente!")
        return redirect('landing:contact')

    return render(request, "landing/contact.html")
