from rest_framework import serializers

from productos.models import Producto
from .models import Carrito, ItemCarrito


class ItemCarritoSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    precio_unitario = serializers.DecimalField(
        source='producto.precio', max_digits=10, decimal_places=2, read_only=True
    )
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = ItemCarrito
        fields = ['id', 'producto', 'producto_nombre', 'precio_unitario', 'cantidad', 'subtotal']

    def get_subtotal(self, obj):
        return obj.cantidad * obj.producto.precio


class CarritoSerializer(serializers.ModelSerializer):
    items = ItemCarritoSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Carrito
        fields = ['id', 'items', 'total']

    def get_total(self, obj):
        return sum(i.cantidad * i.producto.precio for i in obj.items.all())


class AgregarItemSerializer(serializers.Serializer):
    producto = serializers.PrimaryKeyRelatedField(queryset=Producto.objects.all())
    cantidad = serializers.IntegerField(min_value=1)


class ActualizarItemSerializer(serializers.Serializer):
    cantidad = serializers.IntegerField(min_value=1)