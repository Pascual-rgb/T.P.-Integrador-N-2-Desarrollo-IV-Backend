from django.shortcuts import render
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Carrito, ItemCarrito
from .serializers import (
    ActualizarItemSerializer,
    AgregarItemSerializer,
    CarritoSerializer,
)

def obtener_carrito(usuario):
    carrito, _ = Carrito.objects.get_or_create(usuario=usuario)
    return carrito

def validar_stock(producto, cantidad):
    if cantidad > producto.stock:
        raise ValidationError(
            {'cantidad': f'Stock insuficiente. Disponible: {producto.stock}.'}
        )

class CarritoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        carrito = obtener_carrito(request.user)
        return Response(CarritoSerializer(carrito).data)

    def delete(self, request):
        carrito = obtener_carrito(request.user)
        carrito.items.all().delete()
        return Response(CarritoSerializer(carrito).data)

class ItemCarritoCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AgregarItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        producto = serializer.validated_data['producto']
        cantidad = serializer.validated_data['cantidad']

        carrito = obtener_carrito(request.user)
        item = carrito.items.filter(producto=producto).first()

        nueva_cantidad = (item.cantidad if item else 0) + cantidad
        validar_stock(producto, nueva_cantidad)

        if item:
            item.cantidad = nueva_cantidad
            item.save()
        else:
            ItemCarrito.objects.create(
                carrito=carrito, producto=producto, cantidad=cantidad
            )
        return Response(
            CarritoSerializer(carrito).data, status=status.HTTP_201_CREATED
        )

class ItemCarritoDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_item(self, request, pk):
        return get_object_or_404(ItemCarrito, pk=pk, carrito__usuario=request.user)

    def patch(self, request, pk):
        item = self.get_item(request, pk)
        serializer = ActualizarItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cantidad = serializer.validated_data['cantidad']
        validar_stock(item.producto, cantidad)
        item.cantidad = cantidad
        item.save()
        return Response(CarritoSerializer(item.carrito).data)

    def delete(self, request, pk):
        item = self.get_item(request, pk)
        carrito = item.carrito
        item.delete()
        return Response(CarritoSerializer(carrito).data)