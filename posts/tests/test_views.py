from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Follow, Group, Post

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

        self.other_user = User.objects.create_user(username='Votan')
        self.authorized_other_client = Client()
        self.authorized_other_client.force_login(self.other_user)

        self.author = User.objects.get(username='username')
        self.author_authorized_client = Client()
        self.author_authorized_client.force_login(self.author)

    def test_pages_uses_correct_template(self):
        '''URL-адрес использует соответствующий шаблон.'''
        templates_page_names = {
            'posts/index.html': reverse('index'),
            'group.html': reverse(
                'group', kwargs={'slug': PostPagesTest.group.slug}
            ),
            'posts/newpost.html': reverse('new_post'),
            'posts/profile.html': reverse(
                'profile',
                kwargs={'username': self.author}
            ),
            'posts/post.html': reverse(
                'post',
                kwargs={'username': self.author, 'pk': Post.objects.first().pk}
            ),
        }

        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_only_auth_user_add_comment(self):
        '''Только авторизированный пользователь может комментировать посты.'''
        response = self.authorized_client.get(reverse(
            'add_comment',
            kwargs={'username': self.author, 'pk': Post.objects.first().pk}
        ))
        self.assertEqual(response.status_code, 200)

        response = self.guest_client.get(reverse(
            'add_comment',
            kwargs={'username': self.author, 'pk': Post.objects.first().pk}
        ))
        self.assertEqual(response.status_code, 302)

    def test_new_records_add_to_follower(self):
        '''Записи пользователя появляются в ленте подписанта'''

        response_client_one_before = self.authorized_client.get(
            reverse('follow_index')
        )
        response_client_two_before = self.authorized_other_client.get(
            reverse('follow_index')
        )

        Follow.objects.create(user=self.user, author=self.author)

        response_client_one_after = self.authorized_client.get(
            reverse('follow_index')
        )
        response_client_two_after = self.authorized_other_client.get(
            reverse('follow_index')
        )

        self.assertEqual(
            len(response_client_one_before.context.get('page').object_list), 0
        )
        self.assertEqual(
            len(response_client_one_after.context.get('page').object_list), 10
        )
        self.assertEqual(
            len(response_client_two_before.context.get('page').object_list), 0
        )
        self.assertEqual(
            len(response_client_two_after.context.get('page').object_list), 0
        )

    def test_follow_auth_user(self):
        '''Авторизованный может подписываться на других пользователей.'''
        follower_count = self.author.following.count()

        response = self.authorized_client.get(
            reverse('profile_follow', kwargs={
                'username': self.author
            }))

        follower_new_count = self.author.following.count()

        self.assertEqual(response.status_code, 302)
        self.assertTrue(follower_count + 1 == follower_new_count)

    def test_unfollow_auth_user(self):
        '''Авторизованный пользователь может отписываться.'''
        response = self.authorized_client.get(
            reverse('profile_follow', kwargs={
                'username': self.author
            }))

        follower_count = self.author.following.count()

        response = self.authorized_client.get(
            reverse('profile_unfollow', kwargs={
                'username': self.author
            }))

        follower_new_count = self.author.following.count()

        self.assertEqual(response.status_code, 302)
        self.assertTrue(follower_count - 1 == follower_new_count)

    def test_paginator(self):
        '''Проверка работы пажинатора и cach index.html.'''
        templates_reverse = (
            reverse('index'),
            reverse('group', kwargs={'slug': PostPagesTest.group.slug}),
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

        self.assertEqual(response.status_code, 200)
        self.assertEqual(post, response_post)
        self.assertEqual(response.context['author'], PostPagesTest.post.author)

    def test_group_detail_pages_show_correct_context(self):
        '''Шаблон group/<slug:slug>/ сформирован с правильным контекстом.'''
        post = PostPagesTest.post

        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': PostPagesTest.group.slug})
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
                'username': self.author,
                'pk': Post.objects.first().pk
            }))
        response_post = response.context['post']

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
                'username': self.author,
                'pk': Post.objects.last().pk
            }))

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
