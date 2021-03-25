from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class PostURLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_page_not_found(self):
        '''Возвращает ли сервер код 404, если страница не найдена.'''
        response = self.guest_client.get('/missing/1/')
        self.assertEqual(response.status_code, 404)
        response = self.guest_client.get('/missing/')
        self.assertEqual(response.status_code, 404)
