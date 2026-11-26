from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Categoria, Producto
from .serializers import CategoriaSerializer, ProductoSerializer
from .permissions import EsAdminOSoloLectura
from .filters import ProductoFilter
from django.db.models import ProtectedError
from rest_framework import status
from rest_framework.response import Response

def destroy (self, request, *args, **kwargs):
    try:
        return super().destroy(request, *args, **kwargs)
    except ProtectedError:
        return Response({'error': 'No se puede eliminar este objeto porque está siendo utilizado por otros registros.'}, status=status.HTTP_400_BAD_REQUEST)

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [EsAdminOSoloLectura]


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.select_related('categoria').order_by('id')
    serializer_class = ProductoSerializer
    permission_classes = [EsAdminOSoloLectura]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductoFilter
    search_fields = ['nombre']
    ordering_fields = ['precio', 'nombre', 'stock']