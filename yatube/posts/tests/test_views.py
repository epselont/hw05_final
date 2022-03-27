import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Shakespeare')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание',
        )
        cls.group_test_none = Group.objects.create(
            title='Тестовая группа',
            slug='test_group_two',
            description='Тестовое описание группы',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
            image=cls.uploaded
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group_test_none,
            image=cls.uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': f'{self.group.slug}'}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': f'{self.user}'}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post.id}
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html'
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        post_object = response.context['page_obj'].object_list[0]
        post_data = {
            post_object.text: 'Тестовый текст',
            post_object.group.title: 'Тестовая группа',
            post_object.author.username: 'Shakespeare',
            post_object.image: f'{self.post.image}'
        }
        for expected, text in post_data.items():
            with self.subTest(expected=expected):
                self.assertEqual(expected, text)

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list', kwargs={
                    'slug': f'{self.group_test_none.slug}'
                }
            )
        )
        post_object = response.context['page_obj'][0]
        post_data = {
            post_object.text: 'Тестовый текст',
            post_object.group.title: 'Тестовая группа',
            post_object.author.username: 'Shakespeare',
            post_object.image: f'{self.post.image}'
        }
        for expected, text in post_data.items():
            with self.subTest(expected=expected):
                self.assertEqual(expected, text)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:profile', kwargs={'username': f'{self.user}'}
            )
        )
        post_object = response.context['page_obj'][0]
        post_data = {
            post_object.text: 'Тестовый текст',
            post_object.group.title: 'Тестовая группа',
            post_object.author.username: 'Shakespeare',
            post_object.image: f'{self.post.image}'
        }
        for expected, text in post_data.items():
            with self.subTest(expected=expected):
                self.assertEqual(expected, text)

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        post_object = response.context['post']
        post_data = {
            post_object.text: 'Тестовый текст',
            post_object.group.title: 'Тестовая группа',
            post_object.author.username: 'Shakespeare',
            post_object.image: f'{self.post.image}'
        }
        for expected, text in post_data.items():
            with self.subTest(expected=expected):
                self.assertEqual(expected, text)

    def test_create_page_show_correct_context(self):
        """Шаблон create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_pages_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        post_object = response.context['post']
        post_data = {
            post_object.text: 'Тестовый текст',
            post_object.group.title: 'Тестовая группа',
            post_object.author.username: 'Shakespeare'
        }
        for expected, text in post_data.items():
            with self.subTest(expected=expected):
                self.assertEqual(expected, text)

    def test_edit_page_show_correct_context(self):
        """Шаблон create сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_one_post_in_index_group_profile(self):
        """Проверка отдельного поста на страницах
        index, group, profile
        """
        views = [
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': f'{self.group_test_none.slug}'}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': f'{PostPagesTests.user}'}
            )
        ]
        for view in views:
            with self.subTest(view=view):
                response = self.authorized_client.get(view)
                self.assertTrue(
                    self.post in response.context['page_obj'].object_list
                )

    def test_one_post_not_in_another_group(self):
        """Проверка отдельного поста на странице
        другого поста
        """
        response = self.authorized_client.get(
            reverse(
                'posts:group_list', kwargs={'slug': f'{self.group.slug}'}
            )
        )
        self.assertTrue(
            self.post not in response.context['page_obj'].object_list
        )


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Shakespeare')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание',
        )

        for post_num in range(13):
            Post.objects.create(
                author=cls.user,
                text='Тестовый текст',
                group=cls.group
            )

    def test_index_page_list_is_ten_post(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_index_second_page_contains_three_records(self):
        response = self.authorized_client.get(reverse(
            'posts:index') + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_group_list_page_list_is_ten_post(self):
        response = self.authorized_client.get(
            reverse(
                'posts:group_list', kwargs={'slug': f'{self.group.slug}'}
            )
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_group_list_second_page_contains_three_records(self):
        response = self.authorized_client.get(
            reverse(
                'posts:group_list', kwargs={'slug': f'{self.group.slug}'}
            ) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_profile_page_list_is_ten_post(self):
        response = self.authorized_client.get(
            reverse(
                'posts:profile', kwargs={
                    'username': f'{PaginatorViewsTest.user}'
                }
            )
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_profile_second_page_contains_three_records(self):
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={
                    'username': f'{PaginatorViewsTest.user}'
                }
            ) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)
