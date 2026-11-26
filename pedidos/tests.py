from django.test import TestCase
from decimal import Decimal
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from carrito.models import Carrito, ItemCarrito
from productos.models import Categoria, Producto
from .models import ItemPedido, Pedido


class CheckoutTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('ana', 'ana@mail.com', 'ClaveSegura2026')
        self.otro = User.objects.create_user('beto', 'beto@mail.com', 'ClaveSegura2026')
        cat = Categoria.objects.create(nombre='Tortas')
        self.p1 = Producto.objects.create(
            nombre='Torta A', descripcion='d', imagen='http://x.com/a.jpg',
            precio=Decimal('100.00'), categoria=cat, stock=5,
        )
        self.p2 = Producto.objects.create(
            nombre='Torta B', descripcion='d', imagen='http://x.com/b.jpg',
            precio=Decimal('50.00'), categoria=cat, stock=10,
        )
        self.client.force_authenticate(self.user)

    def llenar_carrito(self, usuario, *items):
        carrito, _ = Carrito.objects.get_or_create(usuario=usuario)
        for producto, cantidad in items:
            ItemCarrito.objects.create(carrito=carrito, producto=producto, cantidad=cantidad)
        return carrito

    def test_checkout_sin_token_da_401(self):
        self.client.force_authenticate(None)
        r = self.client.post('/api/pedidos/checkout/')
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_checkout_carrito_vacio(self):
        r = self.client.post('/api/pedidos/checkout/')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Pedido.objects.count(), 0)

    def test_checkout_ok(self):
        carrito = self.llenar_carrito(self.user, (self.p1, 2), (self.p2, 3))
        r = self.client.post('/api/pedidos/checkout/')
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

        pedido = Pedido.objects.get()
        self.assertEqual(pedido.estado, Pedido.Estado.PENDIENTE)
        self.assertEqual(pedido.total, Decimal('350.00'))
        self.assertEqual(pedido.items.count(), 2)

        self.p1.refresh_from_db()
        self.p2.refresh_from_db()
        self.assertEqual(self.p1.stock, 3)
        self.assertEqual(self.p2.stock, 7)

        self.assertEqual(carrito.items.count(), 0)

    def test_precio_unitario_queda_congelado(self):
        self.llenar_carrito(self.user, (self.p1, 1))
        self.client.post('/api/pedidos/checkout/')
        self.p1.precio = Decimal('999.00')
        self.p1.save()
        item = ItemPedido.objects.get()
        self.assertEqual(item.precio_unitario, Decimal('100.00'))

    def test_rollback_si_falta_stock(self):
        carrito = self.llenar_carrito(self.user, (self.p1, 2), (self.p2, 3))
        self.p2.stock = 1
        self.p2.save()

        r = self.client.post('/api/pedidos/checkout/')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(Pedido.objects.count(), 0)
        self.assertEqual(ItemPedido.objects.count(), 0)
        self.p1.refresh_from_db()
        self.assertEqual(self.p1.stock, 5)
        self.assertEqual(carrito.items.count(), 2)

    def test_historial_solo_muestra_pedidos_propios(self):
        self.llenar_carrito(self.user, (self.p1, 1))
        self.client.post('/api/pedidos/checkout/')

        self.client.force_authenticate(self.otro)
        self.llenar_carrito(self.otro, (self.p2, 1))
        self.client.post('/api/pedidos/checkout/')

        r = self.client.get('/api/pedidos/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        pedidos = r.data['results'] if isinstance(r.data, dict) else r.data
        self.assertEqual(len(pedidos), 1)
        self.assertEqual(Pedido.objects.get(pk=pedidos[0]['id']).usuario, self.otro)

    def test_detalle_de_pedido_ajeno_da_404(self):
        self.llenar_carrito(self.user, (self.p1, 1))
        self.client.post('/api/pedidos/checkout/')
        pedido = Pedido.objects.get()

        self.client.force_authenticate(self.otro)
        r = self.client.get(f'/api/pedidos/{pedido.pk}/')
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(r.data['error']['codigo'], 404)