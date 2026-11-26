from rest_framework import serializers
from .models import Categoria, Producto


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion']


class ProductoSerializer(serializers.ModelSerializer):
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

class ProductoSerializer(serializers.ModelSerializer):
    img = serializers.SerializerMethodField()
    categoria = serializers.SlugRelatedField(
        slug_field='nombre', queryset=Categoria.objects.all()
    )
    imagen = serializers.URLField(
        max_length=500, required=False, allow_blank=True, write_only=True
    )
    imagen_archivo = serializers.ImageField(required=False, write_only=True)

    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'descripcion', 'img', 'imagen',
                  'imagen_archivo', 'precio', 'stock', 'categoria']

    def get_img(self, obj):
        if obj.imagen_archivo:
            request = self.context.get('request')
            url = obj.imagen_archivo.url
            return request.build_absolute_uri(url) if request else url
        return obj.imagen

    def validate_precio(self, value):
        if value <= 0:
            raise serializers.ValidationError('El precio debe ser mayor a 0.')
        return value

    def validate(self, attrs):
        if self.instance is None and not attrs.get('imagen') and not attrs.get('imagen_archivo'):
            raise serializers.ValidationError('Subí una imagen o indicá una URL.')
        return attrs