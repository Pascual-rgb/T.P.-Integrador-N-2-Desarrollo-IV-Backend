from rest_framework import serializers
from .models import Categoria, Producto


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion']


class ProductoSerializer(serializers.ModelSerializer):
    # Mantiene los nombres que ya usa el frontend: img y categoria (nombre)
    img = serializers.URLField(source='imagen', max_length=500)
    categoria = serializers.SlugRelatedField(
        slug_field='nombre', queryset=Categoria.objects.all()
    )

    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'descripcion', 'img',
                  'precio', 'stock', 'categoria']

    def validate_precio(self, value):
        if value <= 0:
            raise serializers.ValidationError('El precio debe ser mayor a 0.')
        return value