from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Product, Category

User = get_user_model()


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'image', 'categories']
        labels = {
            'name': 'Nombre del Producto',
            'description': 'Descripción',
            'price': 'Precio ($)',
            'stock': 'Stock disponible',
            'image': 'Imagen del producto',
            'categories': 'Categorías',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full p-3 bg-[#faf9f6] border border-gray-300 focus:border-[#b58a3b] outline-none',
                'placeholder': 'Ej. Pomada Mate BarberBook'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full p-3 bg-[#faf9f6] border border-gray-300 focus:border-[#b58a3b] outline-none',
                'rows': 3,
                'placeholder': 'Describe los beneficios y uso del producto...'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'w-full p-3 bg-[#faf9f6] border border-gray-300 focus:border-[#b58a3b] outline-none',
                'step': '0.01',
                'min': '0.01'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'w-full p-3 bg-[#faf9f6] border border-gray-300 focus:border-[#b58a3b] outline-none',
                'min': '0'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'w-full p-2 bg-[#faf9f6] border border-gray-300'
            }),
            'categories': forms.CheckboxSelectMultiple(attrs={
                'class': 'space-y-1 text-sm text-gray-800'
            }),
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price <= 0:
            raise forms.ValidationError("El precio debe ser mayor a $0.00.")
        return price


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        labels = {
            'name': 'Nombre de la Categoría',
            'description': 'Descripción',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full p-3 bg-[#faf9f6] border border-gray-300 focus:border-[#b58a3b] outline-none',
                'placeholder': 'Ej. Cuidado de Barba'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full p-3 bg-[#faf9f6] border border-gray-300 focus:border-[#b58a3b] outline-none',
                'rows': 3,
                'placeholder': 'Descripción breve de la categoría...'
            }),
        }