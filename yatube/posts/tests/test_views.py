from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='StasBasov')
        group = Group.objects.create(
            title='Заголовок',
            description='Описание',
            slug='test_slug',
        )
        Group.objects.create(
            title='Пусто',
            description='Пустая группа',
            slug='no_posts',
        )

        Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=group,
            pk=1,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
    # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': 'test_slug'}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': 'StasBasov'}): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': 1}): 'posts/post_detail.html',
            reverse('posts:post_edit',
                    kwargs={'pid': 1}): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        # Проверяем, что при обращении к name вызывается соответствующий
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_group_list_show_correct_context(self):
        path = reverse('posts:group_list', kwargs={'slug': 'no_posts'})
        response = self.authorized_client.get(path)
        posts_list = response.context['page_obj']
        self.assertEqual(len(posts_list), 0)

    def test_post_list_pages_show_correct_context(self):
        paths = [reverse('posts:index'),
                 reverse('posts:group_list', kwargs={'slug': 'test_slug'}),
                 reverse('posts:profile', kwargs={'username': 'StasBasov'})]

        for path in paths:
            with self.subTest(path=path):
                response = self.authorized_client.get(path)
                first_object = response.context['page_obj'][0]
                post_text = first_object.text
                post_author = first_object.author.username
                post_group = first_object.group.slug
                post_pk = first_object.pk
                self.assertEqual(post_text, 'Тестовый пост')
                self.assertEqual(post_author, 'StasBasov')
                self.assertEqual(post_group, 'test_slug')
                self.assertEqual(post_pk, 1)

    def test_post_detail(self):
        path = reverse('posts:post_detail', kwargs={'post_id': 1})
        response = self.authorized_client.get(path)
        test_post = response.context['post']
        self.assertEqual(test_post.text, 'Тестовый пост')
        self.assertEqual(test_post.author.username, 'StasBasov')
        self.assertEqual(test_post.group.slug, 'test_slug')
        self.assertEqual(test_post.pk, 1)

    def test_create_form_show_correct_context(self):
        path = reverse('posts:post_create')
        self.form_show_correct_context(path)

    def test_edit_form_show_correct_context(self):
        path = reverse('posts:post_edit', kwargs={'pid': 1})
        self.form_show_correct_context(path)

    def form_show_correct_context(self, path):
        response = self.authorized_client.get(path)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
