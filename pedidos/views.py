from django.shortcuts import render
from decimal import Decimal
from django.db import transaction
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from carrito.models import Carrito
from productos.models import Producto
from .models import ItemPedido, Pedido
from .serializers import PedidoSerializer


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        with transaction.atomic():
            try:
                carrito = Carrito.objects.select_for_update().get(usuario=request.user)
            except Carrito.DoesNotExist:
                raise ValidationError({'carrito': 'El carrito está vacío.'})

            items = list(carrito.items.all())
            if not items:
                raise ValidationError({'carrito': 'El carrito está vacío.'})

            ids = sorted(item.producto_id for item in items)
            productos = {
                p.pk: p
                for p in Producto.objects.select_for_update().filter(pk__in=ids).order_by('pk')
            }

            errores = []
            for item in items:
                producto = productos[item.producto_id]
                if item.cantidad > producto.stock:
                    errores.append(
                        f'{producto.nombre}: pediste {item.cantidad}, '
                        f'disponible {producto.stock}.'
                    )
            if errores:
                raise ValidationError({'stock': errores})

            pedido = Pedido.objects.create(usuario=request.user)
            total = Decimal('0')
            for item in items:
                producto = productos[item.producto_id]
                ItemPedido.objects.create(
                    pedido=pedido,
                    producto=producto,
                    cantidad=item.cantidad,
                    precio_unitario=producto.precio,
                )
                producto.stock -= item.cantidad
                producto.save(update_fields=['stock'])
                total += producto.precio * item.cantidad

            pedido.total = total
            pedido.save(update_fields=['total'])

            carrito.items.all().delete()

        return Response(PedidoSerializer(pedido).data, status=status.HTTP_201_CREATED)


class PedidoListView(generics.ListAPIView):
    serializer_class = PedidoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Pedido.objects.filter(usuario=self.request.user).prefetch_related('items__producto')


class PedidoDetailView(generics.RetrieveAPIView):
    serializer_class = PedidoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Pedido.objects.filter(usuario=self.request.user).prefetch_related('items__producto')