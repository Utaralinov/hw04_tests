from django.contrib.auth import get_user_model

from django.test import TestCase, Client

from ..models import Group, Post


User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим запись в БД для проверки доступности адреса task/test-slug/
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            pk=1
        )

    def setUp(self):
        # Устанавливаем данные для тестирования
        # Создаём экземпляр клиента. Он неавторизован.
        self.guest_client = Client()
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.user)
        self.not_author = User.objects.create(username='NotAuthor')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.not_author)

    def test_unexisting_url(self):
        # Отправляем запрос через client,
        # созданный в setUp()
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)

    def test_url_exist(self):
        urls = ['/',
                '/group/test-slug/',
                '/profile/author/',
                '/posts/1/']

        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_create_url_exists_authorized(self):
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_create_url_redirects_unauthorized_on_login(self):
        response = self.guest_client.get('/create/')
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_edit_url_exists_for_author(self):
        response = self.authorized_client_author.get('/posts/1/edit/')
        self.assertEqual(response.status_code, 200)

    def test_edit_url_redirects_non_author_on_post_detail(self):
        response = self.authorized_client.get('/posts/1/edit/')
        self.assertRedirects(response, '/posts/1/')

    def test_edit_url_redirects_unauthorized_on_login(self):
        response = self.guest_client.get('/posts/1/edit/')
        self.assertRedirects(response, '/auth/login/?next=/posts/1/edit/')

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/author/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/posts/1/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client_author.get(address)
                self.assertTemplateUsed(response, template)
