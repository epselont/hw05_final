import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import CommentForm, PostForm
from posts.models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
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
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group
        )
        cls.comment = Comment.objects.create(
            text='Тестовый комментарий',
            author=cls.user,
            post_id=cls.post.id
        )
        cls.form = PostForm()
        cls.comment_form = CommentForm()
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

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'image': self.uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'posts:profile',
                kwargs={'username': f'{self.user}'}
            )
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                image='posts/small.gif'
            ).exists()
        )

    def test_create_post_not_authorized_client(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, '/auth/login/?next=/create/'
        )
        self.assertEqual(Post.objects.count(), posts_count)

    def test_edite_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Изменённый текст',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': f'{self.post.id}'}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'posts:post_detail',
                kwargs={'post_id': f'{self.post.id}'}
            )
        )
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group']
            ).exists()
        )
        self.assertEqual(Post.objects.count(), posts_count)

    def test_comment_form_authorized_client(self):
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Новый комментарий',
        }
        response = self.authorized_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': f'{self.post.id}'}
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'posts:post_detail',
                kwargs={'post_id': f'{self.post.id}'}
            )
        )
        self.assertTrue(
            Comment.objects.filter(
                text=form_data['text'],
                post_id=self.post.id
            ).exists()
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)

    def test_comment_form_not_authorized_client(self):
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Новый комментарий неизвестного',
        }
        response = self.guest_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': f'{self.post.id}'}
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{self.post.id}/comment/'
        )
        self.assertTrue(
            not Comment.objects.filter(
                text=form_data['text'],
                post_id=self.post.id
            ).exists()
        )
        self.assertEqual(Comment.objects.count(), comment_count)
