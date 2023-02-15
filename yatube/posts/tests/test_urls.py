from django.test import TestCase, Client
from django.contrib.auth import get_user_model

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

    def test_all_users_pages(self):
        """Проверяем, что общедоступные страницы работают"""
        urls = [
            '/', '/group/test-slug/', '/posts/1/', '/profile/User/'
        ]
        for url in urls:
            response = self.guest_client.get(url)  
            self.assertEqual(response.status_code, 200)
    
    # Проверяем страницы доступные авторизовнным пользователям
    def test_create_page(self):
        """Страница /create доступна авторизованным пользователям."""
        response = self.authorized_client.get('/create/')  
        self.assertEqual(response.status_code, 200)

    def test_edit_post_page(self):
        """Страница /post/1/edit доступна авторизованным пользователям."""
        response = self.authorized_client.get('/posts/1/edit/')  
        self.assertEqual(response.status_code, 200)
    
    # Проверяем редиректы для неавторизованного пользователя
    def test_create_page_redirect_if_anonymous(self):
        """Страница /create перенаправляет анонимного пользователя."""
        response = self.guest_client.get('/create/')  
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_edit_post_page_redirect_if_anonymous(self):
        """Страница /post/1/edit перенаправляет анонимного пользователя."""
        response = self.guest_client.get('/posts/1/edit/')  
        self.assertRedirects(response, '/auth/login/?next=/posts/1/edit/')
    
    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/test-slug/',
            'posts/post_detail.html': '/posts/1/',
            'posts/profile.html': '/profile/User/',
            'posts/create_post.html': '/create/',
            'posts/create_post.html': '/posts/1/edit/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template) 
    
    def test_incorrect_page(self):
        """Несуществующая страница не доступна"""
        response = self.authorized_client.get('/posts/2/')  
        self.assertEqual(response.status_code, 404)