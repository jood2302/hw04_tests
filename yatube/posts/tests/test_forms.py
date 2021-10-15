import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post

User = get_user_model()


class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.form = PostForm()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тест группа',
            slug='testgroup',
            description='Тест описание',
        )
        cls.new_group = Group.objects.create(
            title='Тест группа1',
            slug='newtestgroup',
            description='Тест группа',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTest.user)
        self.guest_client = Client()

    def test_create_post(self):
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый заголовок',
            'group': 1,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(self.post.text, PostFormTest.post.text)
        self.assertEqual(self.group, PostFormTest.post.group)
        self.assertEqual(self.post.author, PostFormTest.post.author)
        self.assertEqual(response.status_code, 200)

    def test_edit_post(self):
        PostFormTest.post.refresh_from_db()
        form_data = {
            'text': 'Тест редактирования',
            'group': 1,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={
                'post_id': PostFormTest.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text']
            ).exists()
        )
        self.assertTrue(
            Post.objects.filter(
                group=self.group
            ).exists()
        )
        self.assertTrue(
            Post.objects.filter(
                id=PostFormTest.post.pk
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_guest_client_create_post(self):
        post_count = Post.objects.count()
        form_data = {
            'text': 'Редактирования',
            'group': 1,
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count)
        self.assertRedirects(
            response, reverse('users:login') + '?next=' + reverse(
                'posts:post_create'
            )
        )
