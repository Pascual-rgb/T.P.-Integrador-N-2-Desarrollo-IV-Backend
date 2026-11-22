import django_filters
from .models import Producto


class ProductoFilter(django_filters.FilterSet):
    categoria = django_filters.CharFilter(field_name='categoria__nombre', lookup_expr='iexact')
    precio_min = django_filters.NumberFilter(field_name='precio', lookup_expr='gte')
    precio_max = django_filters.NumberFilter(field_name='precio', lookup_expr='lte')

    class Meta:
        model = Producto
        fields = ['categoria', 'precio_min', 'precio_max']