from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from posts.models import Post, Group

User = get_user_model()

class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='User'
        )
        cls.post = Post.objects.create(
            text='Текст поста',
            author=cls.user
        )
        cls.group = Group.objects.create(
            title='Нзвание группы',
            slug='test-slug',
            description='Описание группы'
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованый клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(StaticURLTests.user)

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names = {
            'posts/index.html': (
                reverse('posts:index')
            ),
            'posts/group_list.html': (
                reverse('posts:group_posts', kwargs={'slug': 'test-slug'})
            ),
            'posts/profile.html': (
                reverse('posts:profile', kwargs={'username': 'User'})
            ),
            'posts/post_detail.html': (
                reverse('posts:post_detail', kwargs={'post_id': 1})
            ),
            'posts/create_post.html': (
                reverse('posts:post_create')
            ),
            'posts/create_post.html': (
                reverse('posts:post_edit', kwargs={'post_id': 1})
            ),
        }
        # Проверяем, что при обращении к name вызывается соответствующий HTML-шаблон
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template) 