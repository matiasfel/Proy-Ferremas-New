from django import forms
from apps.store.models import Product, Category, Brand
from apps.users.models import CustomUser
from django.contrib.auth import get_user_model

User = get_user_model()

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'sku', 'description', 'image', 'price',
            'stock', 'unit', 'category', 'brand',
            'is_featured', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'sku': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'brand': forms.Select(attrs={'class': 'form-select'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        

class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name']

        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Nombre de la marca'}),
        }

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        if not name:
            raise forms.ValidationError("El nombre es obligatorio.")
        return name
    
class UserCreateForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Contraseña"
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone', 'address', 'role', 'is_active', 'is_staff', 'password']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(),
            'is_staff': forms.CheckboxInput(),
        }

class UserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone', 'address', 'role', 'is_active', 'is_staff']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'}),
        }