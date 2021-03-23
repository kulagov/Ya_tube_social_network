from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls.base import reverse

from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    # @classmethod
    # def setUpClass(cls):
    #     super().setUpClass()
    #     cls.status_url = {
    #         '/': 200,
    #         '/group/test-slug/': 200,
    #         '/username/': 200,
    #         '/username/1/': 200,
    #     }
    #     cls.templates_url_names = {
    #         'posts/index.html': '/',
    #         'posts/newpost.html': '/new/',
    #         'group.html': '/group/test-slug/',
    #         'posts/profile.html': '/username/',
    #     }
    #     user = User.objects.create(
    #         password='password',
    #         email='a@a.com',
    #         first_name='first_name',
    #         last_name='last_name',
    #         username='username'
    #     )
    #     group = Group.objects.create(
    #         title='title group',
    #         slug='test-slug',
    #         description='description group'
    #     )
    #     cls.post = Post.objects.create(
    #         text='Тестовый текст',
    #         author=user,
    #         group=group
    #     )

    def setUp(self):
        self.guest_client = Client()
    #     self.user = User.objects.create_user(username='StasBasov')
    #     self.authorized_client = Client()
    #     self.authorized_client.force_login(self.user)
    #     self.author = User.objects.get(username='username')


    def test_page_not_found(self):
        '''Возвращает ли сервер код 404, если страница не найдена.'''
        response = self.guest_client.get('/missing/1/')
        self.assertEqual(response.status_code, 404)
        response = self.guest_client.get('/missing/')
        self.assertEqual(response.status_code, 404) # добаить тест вьюхи с группами, использлвать reverse

