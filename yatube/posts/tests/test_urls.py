from http import HTTPStatus

from django.test import Client, TestCase

from posts.models import Group, Post, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Shakespeare')
        cls.not_author = User.objects.create_user(username='not_author')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=Group.objects.create(
                title='Тестовая группа',
                slug='test_group',
                description='Тестовое описание',
            )
        )
        cls.urls = [
            '/',
            f'/posts/{cls.post.id}/',
            f'/group/{cls.post.group.slug}/',
            f'/profile/{cls.user}/'
        ]

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_not_author = Client()
        self.authorized_client_not_author.force_login(self.not_author)

    def test_posts_urls_guest_client(self):
        """Страницы доступные любому пользователю."""
        for url in PostURLTests.urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_unexisting_page_guest_client(self):
        """Страница /unexisting_page/ недоступна неавторизованному
        пользователю
        """
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_posts_unexisting_page_authorized(self):
        """Страница /unexisting_page/ недоступна авторизованному
        пользователю
        """
        response = self.authorized_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_posts_create_and_post_id_edit_url_authorized(self):
        """Страница /create/ и /posts/1/edit/ доступна авторизованному
        пользователю
        """
        list_url = ['/create/', f'/posts/{self.post.id}/edit/', ]
        for address in list_url:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_post_id_edit_url_not_author(self):
        """Страница /posts/1/edit/ перенаправит не автора
        на страницу /post/1/
        """
        response = self.authorized_client_not_author.get(
            f'/posts/{self.post.id}/edit/', follow=True
        )
        self.assertRedirects(response, f'/posts/{self.post.id}/')

    def test_posts_create_url_redirect_anonymous_on_login(self):
        """Страница /create/ перенаправит анонимного пользователя
        на страницу авторизации.
        """
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.post.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html'
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
