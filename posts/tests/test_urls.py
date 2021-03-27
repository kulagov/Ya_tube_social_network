from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls.base import reverse
from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = User.objects.create(
            password='password',
            email='a@a.com',
            first_name='first_name',
            last_name='last_name',
            username='username'
        )
        group = Group.objects.create(
            title='title group',
            slug='test-slug',
            description='description group'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=user,
            group=group
        )
        cls.status_url = {
            '/': 200,
            f'/group/{group.slug}/': 200,
            f'/{user.username}/': 200,
            f'/{user.username}/{PostURLTests.post.id}/': 200,
        }
        cls.templates_url_names = {
            'posts/index.html': '/',
            'posts/newpost.html': '/new/',
            'group.html': f'/group/{group.slug}/',
            'posts/profile.html': f'/{user.username}/',
        }

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author = User.objects.get(username='username')

    def test_post_list_url_exists_guest_at_desired_location(self):
        '''Общедоступные страницы доступны любому пользователю.'''
        for url, code in PostURLTests.status_url.items():
            with self.subTest(code=code):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, code)

    def test_post_list_url_exists_user_at_desired_location(self):
        '''Доступность страниц авторизованному пользователю.'''
        PostURLTests.status_url['/new/'] = 200

        for url, code in PostURLTests.status_url.items():
            with self.subTest(code=code):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, code)

    def test_urls_uses_correct_template(self):
        '''URL-адрес использует соответствующий шаблон.'''
        for template, url in PostURLTests.templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_post_url_not_exists_guest_for_add(self):
        '''недоступность страницы создания поста для анонима'''
        redirect_part_one = reverse('login')
        redirect_part_two = reverse('new_post')

        response = self.guest_client.get(reverse('new_post'))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            f'{redirect_part_one}?next={redirect_part_two}'
        )

    def test_post_url_not_exists_guest_for_edit(self):
        '''недоступность страницы редактирования поста для анонима'''
        redirect_part_one = reverse('login')
        redirect_part_two = reverse('post_edit', kwargs={
            'username': self.author,
            'pk': self.author.posts.last().id
        })

        response = self.guest_client.get(reverse(
            'post_edit', kwargs={
                'username': self.author,
                'pk': self.author.posts.last().id
            }
        ))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            f'{redirect_part_one}?next={redirect_part_two}'
        )

    def test_post_url_exists_user_for_edit(self):
        '''недоступность страницы редактирования поста для не автора поста.'''
        redirect_to = reverse('post', kwargs={
            'username': self.author.username,
            'pk': self.author.posts.last().id
        })

        response = self.authorized_client.get(reverse(
            'post_edit', kwargs={
                'username': self.author,
                'pk': self.author.posts.last().id
            }
        ))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_to)

    def test_post_url_exists_author_for_edit(self):
        '''доступность страницы редактирования поста для автора поста'''
        author_authorized_client = Client()
        author_authorized_client.force_login(self.author)

        response = author_authorized_client.get(reverse(
            'post_edit', kwargs={
                'username': self.author,
                'pk': self.author.posts.last().id
            }
        ))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'posts/newpost.html')
