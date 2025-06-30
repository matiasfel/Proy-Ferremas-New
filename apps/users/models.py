from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        # Rol por defecto cliente
        if not user.role:
            user.role = 'CLIENTE'
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        # Rol ADMINISTRADOR para superusuario
        extra_fields.setdefault('role', 'ADMINISTRADOR')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superusuario debe tener is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)

class CustomUser(AbstractUser):
    ROLE_CLIENT = 'CLIENTE'
    ROLE_SELLER = 'VENDEDOR'
    ROLE_WAREHOUSE = 'BODEGUERO'
    ROLE_ACCOUNTANT = 'CONTADOR'
    ROLE_ADMIN = 'ADMINISTRADOR'

    ROLE_CHOICES = [
        (ROLE_CLIENT, 'Cliente'),
        (ROLE_SELLER, 'Vendedor'),
        (ROLE_WAREHOUSE, 'Bodeguero'),
        (ROLE_ACCOUNTANT, 'Contador'),
        (ROLE_ADMIN, 'Administrador'),
    ]

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    address = models.CharField(max_length=255, blank=True)
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_CLIENT,
        help_text="Rol del usuario"
    )

    objects = CustomUserManager()

    def __str__(self):
        return self.username