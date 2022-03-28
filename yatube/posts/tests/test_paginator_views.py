from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post
# from yatube.posts.views import profile

User = get_user_model()


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='StasBasov')
        cls.group = Group.objects.create(
            title='Заголовок',
            description='Описание',
            slug='test_slug',
        )
        for i in range(1, 16):
            Post.objects.create(
                author=cls.user,
                text=f'Тестовый пост {i}',
                group=cls.group,
                pk=i,
            )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_homepage_first_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:index'))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_homepage_second_page_contains_five_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 5)

    def test_paginators(self):
        pages_posts_count = {
            reverse('posts:index'): 10,
            reverse('posts:index') + '?page=2': 5,
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}): 10,
            reverse('posts:group_list',
                    kwargs={'slug': 'test_slug'}) + '?page=2': 5,
            reverse('posts:profile', kwargs={'username': 'StasBasov'}): 10,
            reverse('posts:profile',
                    kwargs={'username': 'StasBasov'}) + '?page=2': 5,
        }

        for reverse_name, expected in pages_posts_count.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), expected)
