from django.urls import path
from .views import CheckoutView, PedidoDetailView, PedidoListView

urlpatterns = [
    path('', PedidoListView.as_view(), name='pedidos'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('<int:pk>/', PedidoDetailView.as_view(), name='pedido-detalle'),
]