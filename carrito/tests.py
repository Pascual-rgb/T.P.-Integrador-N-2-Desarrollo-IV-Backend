from django.test import TestCase
from decimal import Decimal
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from productos.models import Categoria, Producto
from .models import Carrito, ItemCarrito


class CarritoTests(APITestCase):
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
            precio=Decimal('50.50'), categoria=cat, stock=10,
        )
        self.client.force_authenticate(self.user)

    def agregar(self, producto, cantidad):
        return self.client.post(
            '/api/carrito/items/',
            {'producto': producto.pk, 'cantidad': cantidad},
            format='json',
        )

    def test_sin_token_da_401(self):
        self.client.force_authenticate(None)
        r = self.client.get('/api/carrito/')
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_carrito_vacio(self):
        r = self.client.get('/api/carrito/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data['items'], [])

    def test_agregar_y_totales(self):
        self.agregar(self.p1, 2)
        r = self.agregar(self.p2, 1)
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        subtotales = sorted(Decimal(str(i['subtotal'])) for i in r.data['items'])
        self.assertEqual(subtotales, [Decimal('50.50'), Decimal('200.00')])
        self.assertEqual(Decimal(str(r.data['total'])), Decimal('250.50'))

    def test_agregar_mas_que_el_stock(self):
        r = self.agregar(self.p1, 6)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('cantidad', r.data['error']['detalles'])

    def test_agregar_dos_veces_suma_y_valida_el_total(self):
        self.agregar(self.p1, 3)
        r = self.agregar(self.p1, 3)  # 3 + 3 = 6 > stock 5
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(ItemCarrito.objects.get().cantidad, 3)

    def test_cantidad_cero_es_invalida(self):
        r = self.agregar(self.p1, 0)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_producto_inexistente(self):
        r = self.client.post(
            '/api/carrito/items/', {'producto': 9999, 'cantidad': 1}, format='json'
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_actualizar_cantidad(self):
        self.agregar(self.p1, 1)
        item = ItemCarrito.objects.get()
        r = self.client.patch(
            f'/api/carrito/items/{item.pk}/', {'cantidad': 4}, format='json'
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        item.refresh_from_db()
        self.assertEqual(item.cantidad, 4)

    def test_actualizar_sobre_el_stock(self):
        self.agregar(self.p1, 1)
        item = ItemCarrito.objects.get()
        r = self.client.patch(
            f'/api/carrito/items/{item.pk}/', {'cantidad': 99}, format='json'
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_eliminar_item(self):
        self.agregar(self.p1, 1)
        item = ItemCarrito.objects.get()
        r = self.client.delete(f'/api/carrito/items/{item.pk}/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(ItemCarrito.objects.count(), 0)

    def test_vaciar_carrito(self):
        self.agregar(self.p1, 1)
        self.agregar(self.p2, 1)
        r = self.client.delete('/api/carrito/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(ItemCarrito.objects.count(), 0)

    def test_item_de_otro_usuario_da_404(self):
        carrito_ajeno = Carrito.objects.create(usuario=self.otro)
        item = ItemCarrito.objects.create(
            carrito=carrito_ajeno, producto=self.p1, cantidad=1
        )
        r = self.client.patch(
            f'/api/carrito/items/{item.pk}/', {'cantidad': 2}, format='json'
        )
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)
        r = self.client.delete(f'/api/carrito/items/{item.pk}/')
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)
        item.refresh_from_db()
        self.assertEqual(item.cantidad, 1)