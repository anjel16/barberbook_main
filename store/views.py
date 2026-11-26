from uuid import UUID
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseForbidden

from .forms import RegisterForm, ProductForm, CategoryForm
from .models import User, Product, Category, Cart, CartItem


def tiene_permiso_panel(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser or getattr(user, 'is_seller', False))


# =====================================
# INICIO Y CATÁLOGO DE PRODUCTOS
# =====================================
def home(request):
    products = Product.objects.select_related('owner').prefetch_related('categories').order_by('-created_at')

    q = request.GET.get('q', '').strip()
    if q:
        products = products.filter(Q(name__icontains=q) | Q(description__icontains=q))

    category = request.GET.get('category', '')
    if category:
        try:
            category_uuid = UUID(category)
            products = products.filter(categories__id=category_uuid)
        except ValueError:
            pass

    products = products.distinct()
    categories = Category.objects.all()

    paginator = Paginator(products, 9)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'store/home.html', {
        'products': page_obj,
        'categories': categories,
        'page_obj': page_obj,
    })


# =====================================
# REGISTRO E INICIO DE SESIÓN
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
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = RegisterForm()

    return render(request, 'store/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard' if tiene_permiso_panel(request.user) else 'home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenido a BarberBook, {user.username}!')
            if tiene_permiso_panel(user):
                return redirect('dashboard')
            return redirect('home')

        messages.error(request, 'Usuario o contraseña incorrectos. Verifica tus datos.')

    return render(request, 'store/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión correctamente.')
    return redirect('home')


# =====================================
# 📊 DASHBOARD ADMINISTRATIVO
# =====================================
@login_required(login_url='login')
def dashboard(request):
    if not tiene_permiso_panel(request.user):
        return HttpResponseForbidden("Acceso denegado: Se requieren permisos de Administrador o Vendedor.")

    if request.user.is_staff or request.user.is_superuser:
        products = Product.objects.select_related('owner').all().order_by('-created_at')
    else:
        products = Product.objects.filter(owner=request.user).order_by('-created_at')

    categories = Category.objects.all()

    context = {
        'products': products,
        'categories': categories,
        'total_users': User.objects.count(),
        'total_products': Product.objects.count(),
        'total_categories': Category.objects.count(),
        'total_carts': Cart.objects.count(),
    }
    return render(request, 'store/dashboard.html', context)


# =====================================
# 📦 CRUD PRODUCTOS
# =====================================
@login_required(login_url='login')
def product_create(request):
    if not tiene_permiso_panel(request.user):
        return HttpResponseForbidden("No tienes permisos para registrar productos.")

    form = ProductForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        product = form.save(commit=False)
        product.owner = request.user
        product.save()
        form.save_m2m()
        messages.success(request, 'Producto registrado correctamente.')
        return redirect('dashboard')

    return render(request, 'store/product_form.html', {'form': form, 'titulo': 'Nuevo Producto'})


@login_required(login_url='login')
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if not (request.user.is_staff or request.user.is_superuser or product.owner == request.user):
        return HttpResponseForbidden("No tienes permisos para editar este producto.")

    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if form.is_valid():
        form.save()
        messages.success(request, 'Producto actualizado correctamente.')
        return redirect('dashboard')

    return render(request, 'store/product_form.html', {'form': form, 'titulo': 'Editar Producto'})


@login_required(login_url='login')
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if not (request.user.is_staff or request.user.is_superuser or product.owner == request.user):
        return HttpResponseForbidden("No tienes permisos para eliminar este producto.")

    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Producto eliminado de la base de datos.')
        return redirect('dashboard')

    return render(request, 'store/product_confirm_delete.html', {'product': product, 'tipo': 'producto'})


# =====================================
# 🏷️ CRUD CATEGORÍAS
# =====================================
@login_required(login_url='login')
def category_create(request):
    if not tiene_permiso_panel(request.user):
        return HttpResponseForbidden("No tienes permisos para crear categorías.")

    form = CategoryForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Categoría creada correctamente.')
        return redirect('dashboard')

    return render(request, 'store/product_form.html', {'form': form, 'titulo': 'Nueva Categoría'})


@login_required(login_url='login')
def category_update(request, pk):
    if not tiene_permiso_panel(request.user):
        return HttpResponseForbidden("No tienes permisos para editar categorías.")

    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=category)
    if form.is_valid():
        form.save()
        messages.success(request, 'Categoría actualizada correctamente.')
        return redirect('dashboard')

    return render(request, 'store/product_form.html', {'form': form, 'titulo': 'Editar Categoría'})


@login_required(login_url='login')
def category_delete(request, pk):
    if not tiene_permiso_panel(request.user):
        return HttpResponseForbidden("No tienes permisos para eliminar categorías.")

    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Categoría eliminada correctamente.')
        return redirect('dashboard')

    return render(request, 'store/product_confirm_delete.html', {'product': category, 'tipo': 'categoría'})


# =====================================
# 🛒 CARRITO DE COMPRAS
# =====================================
@login_required(login_url='login')
def cart_detail(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = CartItem.objects.filter(cart=cart).select_related('product')
    total = sum(item.product.price * item.quantity for item in items)

    return render(request, 'store/cart.html', {
        'cart': cart,
        'items': items,
        'total': total,
    })


@login_required(login_url='login')
def cart_add(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if product.stock <= 0:
        messages.error(request, 'Este producto está agotado.')
        return redirect('home')

    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        if item.quantity < product.stock:
            item.quantity += 1
            item.save()
        else:
            messages.error(request, f'Solo hay {product.stock} unidades disponibles en stock.')
            return redirect('home')

    messages.success(request, f'"{product.name}" se agregó a tu carrito.')
    return redirect('cart_detail')


@login_required(login_url='login')
def cart_remove(request, pk):
    item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
    item.delete()
    messages.success(request, 'Producto eliminado del carrito.')
    return redirect('cart_detail')