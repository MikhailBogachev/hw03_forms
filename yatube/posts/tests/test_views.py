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
        cls.group = Group.objects.create(
            title='Название группы',
            slug='test-slug',
            description='Описание группы'
        )
        cls.post = Post.objects.create(
            text='Текст поста',
            author=cls.user,
            group=cls.group
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
                reverse('posts:group_list', kwargs={'slug': 'test-slug'})
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

    def test_index_page_correct_context(self):
        """Шаблон index сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        task_text = first_object.text
        task_author = first_object.author.username
        task_group = first_object.group.title

        self.assertEqual(task_text, 'Текст поста')
        self.assertEqual(task_author, 'User')
        self.assertEqual(task_group, 'Название группы')

    
    def test_group_page_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'})
        )
        first_object = response.context['page_obj'][0]
        group_object = response.context['group']

        task_post_text = first_object.text
        task_post_author = first_object.author.username
        task_post_group = first_object.group.title
        task_group_title = group_object.title
        task_group_slug = group_object.slug
        task_group_description = group_object.description

        self.assertEqual(task_post_text, 'Текст поста')
        self.assertEqual(task_post_author, 'User')
        self.assertEqual(task_post_group, 'Название группы')
        self.assertEqual(task_group_title, 'Название группы')
        self.assertEqual(task_group_slug, 'test-slug')
        self.assertEqual(task_group_description, 'Описание группы')       

    