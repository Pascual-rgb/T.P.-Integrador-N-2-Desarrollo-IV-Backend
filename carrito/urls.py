from django.urls import path

from .views import CarritoView, ItemCarritoCreateView, ItemCarritoDetailView

urlpatterns = [
    path('', CarritoView.as_view(), name='carrito'),
    path('items/', ItemCarritoCreateView.as_view(), name='carrito-items'),
    path('items/<int:pk>/', ItemCarritoDetailView.as_view(), name='carrito-item'),
]