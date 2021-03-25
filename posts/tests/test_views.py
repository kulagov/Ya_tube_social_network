from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostPagesTest(TestCase):
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
        cls.group = Group.objects.create(
            title='title group',
            slug='test-slug',
            description='description group'
        )

        post_list = (Post(
            text='Тестовый текст',
            author=user,
            group=cls.group
        ) for _ in range(13))
        Post.objects.bulk_create(post_list)

        cls.post = Post.objects.first()

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author = User.objects.get(username='username')
        self.author_authorized_client = Client()
        self.author_authorized_client.force_login(self.author)

    def test_pages_uses_correct_template(self):
        '''URL-адрес использует соответствующий шаблон.'''
        templates_page_names = {
            'posts/index.html': reverse('index'),
            'group.html': reverse('group', kwargs={'slug': 'test-slug'}),
            'posts/newpost.html': reverse('new_post'),
            'posts/profile.html': reverse(
                'profile',
                kwargs={'username': 'username'}
            ),
            'posts/post.html': reverse(
                'post',
                kwargs={'username': 'username', 'pk': Post.objects.first().pk}
            ),
        }

        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

# FIXME
    def test_follow_auth_user(self):
        '''Авторизованный может подписываться и отписываться на других.'''
        follower_count = self.author.follower.count()
        print(follower_count)
        response = self.authorized_client.get(
            reverse('profile_follow'), username=self.author.username
        )
        follower_count = self.author.follower.count()
        print(follower_count)
        print(response.status_code)


    def test_paginator(self):
        '''Проверка работы "пажинатора" и cach index.html.'''
        templates_reverse = (
            reverse('index'),
            reverse('group', kwargs={'slug': 'test-slug'}),
            reverse('profile', kwargs={'username': self.author})
        )

        for reverse_name in templates_reverse:
            with self.subTest(reverse_name=f'{reverse_name} and next...'):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(
                    len(response.context.get('page').object_list), 10
                )
                response = self.guest_client.get(reverse_name + '?page=2')
                self.assertEqual(
                    len(response.context.get('page').object_list), 3
                )
        # проверка cach
            # last_text = Post.objects.last()
            # print('!!!!!!!', last_text.text)
            # last_text.text = 'Новый текст'
            # Post.objects.bulk_update((last_text,),('text',))
            # # Post.objects.last().

            # last_text = Post.objects.last()

            # print('!!!!!!!', last_text.text)
            # response = self.guest_client.get(reverse('index'))
            # response_post = response.context.get('object_list')[0]
            # print(response_post)
        # Post

        # self.assertEqual(
        #     len(response.context.get('page').object_list), 10
        # )

    def test_index_page_show_correct_context(self):
        '''Шаблон index сформирован с правильным контекстом.'''
        post = PostPagesTest.post

        response = self.authorized_client.get(reverse('index'))

        response_post = response.context.get('object_list')[0]

        self.assertEqual(post, response_post)

    def test_profile_page_show_correct_context(self):
        '''Шаблон profile сформирован с правильным контекстом.'''
        post = PostPagesTest.post

        response = self.authorized_client.get(
            reverse('profile', kwargs={'username': post.author})
        )

        response_post = response.context['object_list'][0]

        # auth_card = {
        #     'records': Post.objects.count(),
        #     'subscribers': 'FIXME',
        #     'subscribed': 'FIXME',
        # }

        self.assertEqual(response.status_code, 200)
        self.assertEqual(post, response_post)
        self.assertEqual(response.context['author'], PostPagesTest.post.author)

    def test_group_detail_pages_show_correct_context(self):
        '''Шаблон group/<slug:slug>/ сформирован с правильным контекстом.'''
        post = PostPagesTest.post

        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': 'test-slug'})
        )

        response_post = response.context.get('object_list')[0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(post, response_post)
        self.assertEqual(response.context['group'], PostPagesTest.group)

    def test_post_id_page_show_correct_context(self):
        '''Шаблон отдельного поста post сформирован с правильным контекстом.'''
        post = PostPagesTest.post

        response = self.authorized_client.get(
            reverse('post', kwargs={
                'username': 'username',
                'pk': Post.objects.first().pk
            }))
        response_post = response.context['post']

        auth_card = {
            'records': Post.objects.count(),
            'subscribers': 'FIXME',
            'subscribed': 'FIXME',
        }

        self.assertEqual(post, response_post)
        self.assertEqual(response.context['author'], PostPagesTest.post.author)

    def test_new_post_show_correct_context(self):
        '''Шаблон new_post сформирован с правильным контекстом.'''
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }

        response = self.authorized_client.get(reverse('new_post'))

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_edit_post_show_correct_context(self):
        '''Шаблон new_post для ред. поста сформирован с правильным конекст.'''
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }

        response = self.author_authorized_client.get(
            reverse('post_edit', kwargs={
                'username': 'username',
                'pk': Post.objects.last().pk
            }))

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
