from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase


class RegistroTests(APITestCase):
    url = '/api/auth/registro/'

    def datos(self, **cambios):
        base = {
            'username': 'cliente1',
            'email': 'cliente1@mail.com',
            'password': 'ClaveSegura2026',
            'password2': 'ClaveSegura2026',
        }
        base.update(cambios)
        return base

    def test_registro_ok_y_password_hasheada(self):
        r = self.client.post(self.url, self.datos(), format='json')
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertNotIn('password', r.data)
        usuario = User.objects.get(username='cliente1')
        self.assertNotEqual(usuario.password, 'ClaveSegura2026')
        self.assertTrue(usuario.check_password('ClaveSegura2026'))

    def test_email_duplicado(self):
        self.client.post(self.url, self.datos(), format='json')
        r = self.client.post(
            self.url, self.datos(username='otro', email='CLIENTE1@mail.com'), format='json'
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', r.data['error']['detalles'])

    def test_password_debil(self):
        r = self.client.post(
            self.url, self.datos(password='1234', password2='1234'), format='json'
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', r.data['error']['detalles'])

    def test_passwords_distintas(self):
        r = self.client.post(self.url, self.datos(password2='OtraClave2026'), format='json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_devuelve_tokens(self):
        self.client.post(self.url, self.datos(), format='json')
        r = self.client.post(
            '/api/auth/login/',
            {'username': 'cliente1', 'password': 'ClaveSegura2026'},
            format='json',
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertIn('access', r.data)
        self.assertIn('refresh', r.data)

    def test_login_incorrecto_da_401(self):
        r = self.client.post(
            '/api/auth/login/', {'username': 'nadie', 'password': 'x'}, format='json'
        )
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(r.data['error']['codigo'], 401)