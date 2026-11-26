from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from .models import Mensaje


class ContactoAPITests(APITestCase):
    def setUp(self):
        self.url = '/api/contacto/'
        self.admin = User.objects.create_user('admin_test', password='Clave12345!', is_staff=True)

    def test_mensaje_valido_se_guarda(self):
        datos = {'nombre': 'María Pérez', 'correo': 'maria@ejemplo.com',
                 'mensaje': 'Quisiera encargar una torta.'}
        r = self.client.post(self.url, datos, format='json')
        self.assertEqual(r.status_code, 201)
        self.assertEqual(Mensaje.objects.count(), 1)
        self.assertFalse(Mensaje.objects.first().leido)

    def test_mensaje_invalido_devuelve_400(self):
        datos = {'nombre': 'A', 'correo': 'no-es-un-correo', 'mensaje': 'hola'}
        r = self.client.post(self.url, datos, format='json')
        self.assertEqual(r.status_code, 400)
        self.assertIn('correo', r.data)

    def test_sin_credenciales_no_puede_listar(self):
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 401)

    def test_admin_puede_listar_y_marcar_como_leido(self):
        mensaje = Mensaje.objects.create(
            nombre='Ana', correo='ana@ejemplo.com', mensaje='Mensaje de prueba largo.')
        self.client.force_authenticate(user=self.admin)
        self.assertEqual(self.client.get(self.url).status_code, 200)
        r = self.client.patch(f'{self.url}{mensaje.id}/', {'leido': True}, format='json')
        self.assertEqual(r.status_code, 200)
        mensaje.refresh_from_db()
        self.assertTrue(mensaje.leido)