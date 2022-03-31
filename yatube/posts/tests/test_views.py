from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='StasBasov')
        cls.group = Group.objects.create(
            title='Заголовок',
            description='Описание',
            slug='test_slug',
        )
        cls.empty_group = Group.objects.create(
            title='Пусто',
            description='Пустая группа',
            slug='no_posts',
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username':
                            self.user.username}): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id':
                            self.post.pk}): 'posts/post_detail.html',
            reverse('posts:post_edit',
                    kwargs={'pid': self.post.pk}): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_group_list_show_correct_context(self):
        path = reverse('posts:group_list',
                       kwargs={'slug': self.empty_group.slug})
        response = self.authorized_client.get(path)
        posts_list = response.context['page_obj']
        self.assertEqual(len(posts_list), 0)

    def test_post_list_pages_show_correct_context(self):
        paths = [reverse('posts:index'),
                 reverse('posts:group_list', kwargs={'slug': self.group.slug}),
                 reverse('posts:profile',
                         kwargs={'username': self.user.username})]

        for path in paths:
            with self.subTest(path=path):
                response = self.authorized_client.get(path)
                first_object = response.context['page_obj'][0]
                self.check_post_detail(first_object)

    def test_post_detail(self):
        path = reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
        response = self.authorized_client.get(path)
        test_post = response.context['post']
        self.check_post_detail(test_post)

    def check_post_detail(self, post):
        self.assertEqual(post.pk, self.post.pk)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author.username, self.user.username)
        self.assertEqual(post.group.slug, self.group.slug)

    def test_create_form_show_correct_context(self):
        path = reverse('posts:post_create')
        self.form_show_correct_context(path)

    def test_edit_form_show_correct_context(self):
        path = reverse('posts:post_edit', kwargs={'pid': self.post.pk})
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
