from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from uuid import UUID
from .forms import RegisterForm
from .models import Product, Category
from django.shortcuts import render
from django.shortcuts import render, redirect
from .models import Product

def product_create(request):
    if request.method == 'POST':
        # Aquí irá el código para guardar el producto
        pass
    return render(request, 'store/product_form.html')

def dashboard(request):
    return render(request, 'store/dashboard.html')

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

            messages.success(
                request,
                '¡Tu cuenta fue creada correctamente!'
            )

            return redirect('home')

    else:
        form = RegisterForm()

    return render(
        request,
        'store/register.html',
        {'form': form}
    )


# =====================================
# INICIO DE SESIÓN
# =====================================

def login_view(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            messages.success(
                request,
                '¡Bienvenido a BarberBook!'
            )

            return redirect('home')

        messages.error(
            request,
            'Usuario o contraseña incorrectos.'
        )

    return render(request, 'store/login.html')


# =====================================
# CERRAR SESIÓN
# =====================================

def logout_view(request):

    logout(request)

    messages.success(
        request,
        'Has cerrado sesión correctamente.'
    )

    return redirect('home')