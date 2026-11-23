from uuid import UUID
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseForbidden

from .forms import RegisterForm, ProductForm
from .models import Product, Category


# =====================================
# INICIO Y CATÁLOGO DE PRODUCTOS
# =====================================

def home(request):
    products = Product.objects.select_related(
        'owner'
    ).prefetch_related(
        'categories'
    ).all()

    # Buscador
    q = request.GET.get('q', '').strip()
    if q:
        products = products.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q)
        )

    # Filtro por categoría UUID
    category = request.GET.get('category', '')
    if category:
        try:
            category_uuid = UUID(category)
            products = products.filter(
                categories__id=category_uuid
            )
        except ValueError:
            pass

    products = products.distinct()

    # Obtener categorías
    categories = Category.objects.all()

    # Paginación
    paginator = Paginator(products, 9)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(
        request,
        'store/home.html',
        {
            'products': page_obj,
            'categories': categories,
            'page_obj': page_obj,
        }
    )


# =====================================
# REGISTRO DE USUARIOS
# =====================================

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '¡Tu cuenta fue creada correctamente!')
            return redirect('home')
    else:
        form = RegisterForm()

    return render(request, 'store/register.html', {'form': form})


# =====================================
# INICIO DE SESIÓN
# =====================================

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, '¡Bienvenido a BarberBook!')
            return redirect('home')

        messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'store/login.html')


# =====================================
# CERRAR SESIÓN
# =====================================

def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión correctamente.')
    return redirect('home')


# =====================================
# 📊 DASHBOARD DE VENDEDOR
# =====================================

@login_required
def dashboard(request):
    if not getattr(request.user, 'is_seller', False):
        return HttpResponseForbidden("No tienes permisos")

    products = Product.objects.filter(owner=request.user)

    return render(request, 'store/dashboard.html', {
        'products': products
    })


# =====================================
# ➕ CREAR PRODUCTO
# =====================================

@login_required
def product_create(request):
    if not getattr(request.user, 'is_seller', False):
        return HttpResponseForbidden("Solo vendedores")

    form = ProductForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        product = form.save(commit=False)
        product.owner = request.user
        product.save()
        form.save_m2m()  # Guarda las categorías (ManyToMany)

        messages.success(request, 'Producto creado correctamente.')
        return redirect('dashboard')

    return render(request, 'store/product_form.html', {'form': form})


# =====================================
# ✏️ EDITAR PRODUCTO
# =====================================

@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if product.owner != request.user:
        return HttpResponseForbidden("No puedes editar este producto")

    form = ProductForm(request.POST or None, request.FILES or None, instance=product)

    if form.is_valid():
        form.save()
        messages.success(request, 'Producto actualizado.')
        return redirect('dashboard')

    return render(request, 'store/product_form.html', {'form': form})


# =====================================
# 🗑️ ELIMINAR PRODUCTO
# =====================================

@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if product.owner != request.user:
        return HttpResponseForbidden("No puedes eliminar este producto")

    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Producto eliminado.')
        return redirect('dashboard')

    return render(request, 'store/product_confirm_delete.html', {'product': product})

def cart_detail(request):
    # Vista temporal hasta que implementes el carrito completo
    return render(request, 'store/home.html')