from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Auth
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Productos CRUD
    path('products/create/', views.product_create, name='product_create'),
    path('products/<uuid:pk>/edit/', views.product_update, name='product_update'),
    path('products/<uuid:pk>/delete/', views.product_delete, name='product_delete'),

    # Categorías CRUD
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<uuid:pk>/edit/', views.category_update, name='category_update'),
    path('categories/<uuid:pk>/delete/', views.category_delete, name='category_delete'),

    # Carrito
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<uuid:pk>/', views.cart_add, name='cart_add'),
    path('cart/remove/<uuid:pk>/', views.cart_remove, name='cart_remove'),
]