import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Group, Post, User


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.group = Group.objects.create(
            title='title group',
            slug='test-slug',
            description='description group'
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        '''Валидная форма создает запись в Post.'''
        post_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        post_data = {
            'text': 'Тестовый текст',
            'group': PostCreateFormTests.group.id,
            'image': uploaded
        }

        add_post = self.authorized_client.post(
            reverse('new_post'),
            data=post_data,
            follow=True
        )

        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст',
                group=PostCreateFormTests.group.id,
                author=self.user,
                image='posts/small.gif'
            ).exists()
        )
        self.assertEqual(add_post.status_code, 200)

    def test_update_post(self):
        '''Валидная форма обновляет запись в Post.'''
        post = Post.objects.create(
            text='Тестовый текст',
            group=PostCreateFormTests.group,
            author=self.user
        )
        update_data = {
            'text': 'Измененный текст',
        }
        update_post = self.authorized_client.post(
            reverse('post_edit', kwargs={
                'username': self.user,
                'pk': post.id
            }),
            data=update_data,
            follow=True
        )

        self.assertTrue(
            Post.objects.filter(
                text='Измененный текст',
                group=None,
                author=self.user
            ).exists()
        )
        self.assertEqual(update_post.status_code, 200)
