from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class AboutURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.status_url = {
            '/about/author/': 200,
            '/about/tech/': 200,
        }
        cls.templates_url_names = {
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/',
        }

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_list_url_exists_guest_at_desired_location(self):
        '''Cтраницы author, tech доступны любому пользователю.'''
        for url, code in AboutURLTests.status_url.items():
            with self.subTest(code=code):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, code)

    def test_urls_uses_correct_template(self):
        '''URL-адрес использует соответствующий шаблон.'''
        for template, url in AboutURLTests.templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
