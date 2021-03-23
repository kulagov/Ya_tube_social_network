from django.test import TestCase

from posts.models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            password='password',
            email='a@a.com',
            first_name='first_name',
            last_name='last_name',
            username='username'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user
        )

    def test_verbose_name(self):
        '''verbose_name в полях совпадает с ожидаемым.'''
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст',
            'pub_date': 'Дата публикации',
        }

        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        '''help_text в полях совпадает с ожидаемым.'''
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Введите Ваш текст',
            'author': 'Автор поста',
        }

        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_object_post_name_is_title_field(self):
        '''В поле __str__  объекта post записано значение
        поля post.text[:15].'''
        post = PostModelTest.post

        expected_object_name = post.text[:15]

        self.assertEqual(expected_object_name, str(post))


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Гр' * 105,
            description='description'
        )

    def test_verbose_name(self):
        '''verbose_name в полях совпадает с ожидаемым.'''
        group = GroupModelTest.group
        field_verboses = {
            'title': 'Название группы',
            'description': 'Описание группы',
        }

        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)

    def test_object_group_name_is_title_field(self):
        '''В поле __str__  объекта group записано значение поля group.title.'''
        group = GroupModelTest.group
        expected_object_name = group.title

        self.assertEqual(expected_object_name, str(group))
