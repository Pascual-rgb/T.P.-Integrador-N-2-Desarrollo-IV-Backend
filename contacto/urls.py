from django.urls import path
from .views import MensajeListCreateView, MensajeDetailView


urlpatterns = [
    path('', MensajeListCreateView.as_view(), name='contacto'),
    path('<int:pk>/', MensajeDetailView.as_view(), name='contacto-detail'),
]