from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='Author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание группы'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост'
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Новый пост',
            'group': self.group.pk
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        path = reverse('posts:profile',
                       kwargs={'username': self.user.username})
        self.assertRedirects(response, path)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        last_post = Post.objects.all().order_by('pk').last()
        self.assertEqual(last_post.text, form_data['text'])
        self.assertEqual(last_post.author, self.user)
        self.assertEqual(last_post.group, self.group)

    def test_edit_post(self):
        path = reverse(('posts:post_detail'), kwargs={'post_id': self.post.pk})
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Новый текст поста',
            'group': self.group.pk
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'pid': self.post.pk}),
            data=form_data,
            follow=True
        )
        edited_post = get_object_or_404(Post, pk=self.post.pk)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertRedirects(response, path)
        self.assertEqual(edited_post.text, form_data['text'])
        self.assertEqual(edited_post.group, self.group)
