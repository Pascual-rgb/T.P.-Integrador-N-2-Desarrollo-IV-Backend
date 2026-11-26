from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from .models import Categoria, Producto


class ProductoAPITests(APITestCase):
    def setUp(self):
        self.tortas = Categoria.objects.create(nombre='Tortas')
        self.tartas = Categoria.objects.create(nombre='Tartas')
        for nombre, precio, stock, cat in [
            ('Torta de Chocolate', 25000, 10, self.tortas),
            ('Lemon Pie', 9500, 9, self.tartas),
            ('Chocotorta', 32000, 15, self.tortas),
        ]:
            Producto.objects.create(
                nombre=nombre, descripcion='Descripción de prueba',
                imagen='https://ejemplo.com/foto.jpg',
                precio=precio, stock=stock, categoria=cat,
            )
        self.admin = User.objects.create_user('admin_test', password='Clave12345!', is_staff=True)
        self.cliente = User.objects.create_user('cliente_test', password='Clave12345!')
        self.url = '/api/productos/'
        self.datos_nuevos = {
            'nombre': 'Torta Nueva', 'descripcion': 'Prueba',
            'imagen': 'https://ejemplo.com/nueva.jpg',
            'precio': 12000, 'stock': 5, 'categoria': 'Tortas',
        }

    def test_listado_publico(self):
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['count'], 3)

    def test_filtro_por_categoria(self):
        r = self.client.get(self.url, {'categoria': 'Tortas'})
        self.assertEqual(r.data['count'], 2)

    def test_filtro_por_rango_de_precio(self):
        r = self.client.get(self.url, {'precio_min': 10000, 'precio_max': 26000})
        self.assertEqual(r.data['count'], 1)
        self.assertEqual(r.data['results'][0]['nombre'], 'Torta de Chocolate')

    def test_busqueda_por_nombre(self):
        r = self.client.get(self.url, {'search': 'lemon'})
        self.assertEqual(r.data['count'], 1)

    def test_ordenamiento_por_precio_descendente(self):
        r = self.client.get(self.url, {'ordering': '-precio'})
        self.assertEqual(r.data['results'][0]['nombre'], 'Chocotorta')

    def test_sin_credenciales_no_puede_crear(self):
        r = self.client.post(self.url, self.datos_nuevos, format='json')
        self.assertEqual(r.status_code, 401)

    def test_usuario_comun_no_puede_crear(self):
        self.client.force_authenticate(user=self.cliente)
        r = self.client.post(self.url, self.datos_nuevos, format='json')
        self.assertEqual(r.status_code, 403)

    def test_admin_puede_crear(self):
        self.client.force_authenticate(user=self.admin)
        r = self.client.post(self.url, self.datos_nuevos, format='json')
        self.assertEqual(r.status_code, 201)
        self.assertEqual(Producto.objects.count(), 4)

    def test_admin_no_puede_crear_con_precio_invalido(self):
        self.client.force_authenticate(user=self.admin)
        datos = {**self.datos_nuevos, 'precio': 0}
        r = self.client.post(self.url, datos, format='json')
        self.assertEqual(r.status_code, 400)

    def test_admin_puede_eliminar(self):
        self.client.force_authenticate(user=self.admin)
        producto = Producto.objects.first()
        r = self.client.delete(f'{self.url}{producto.id}/')
        self.assertEqual(r.status_code, 204)