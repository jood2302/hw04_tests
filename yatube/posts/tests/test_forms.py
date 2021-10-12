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
        cls.user = User.objects.create_user(username = 'test_user')
        cls.group = Group.objects.create(
            title = 'Тест группа',
            slug = 'testgroup',
            description = 'Тест описание',
        )
        cls.new_group = Group.objects.create(
            title = 'Тест группа1',
            slug = 'newtestgroup',
            description = 'Тест группа',
        )
        cls.post = Post.objects.create(
            text = 'Тестовый текст',
            author = cls.user,
            group = cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTest.user)

    def test_create_post(self):
        posts_count = Post.objects.count()
        post_data = {
            'text': 'Новый тест',
            'group': PostFormTest.group.id,
        }

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=post_data,
            follow=True,
        )

        self.assertRedirects(response,
                             reverse('posts:profile',
                                     kwargs={"username": "test_user"}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(Post.objects.get(pk=2).text, 'Новый тест')
        self.assertEqual(Post.objects.get(pk=2).group.id, self.group.id)
        self.assertEqual(Post.objects.get(pk=2).author.username, "test_user")

    def test_edit_post(self):
        post_id = PostFormTest.post.id
        post_data = {
            'text': 'Новый тест',
            'group': PostFormTest.new_group.id,
        }
        kwargs_post = {
            'post_id': post_id,
        }

        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs=kwargs_post),
            data=post_data,
            follow=True,
        )

        self.assertRedirects(response,
                             reverse('posts:post_detail', kwargs=kwargs_post))
        self.assertEqual(Post.objects.get(id=post_id).text, post_data['text'])
        self.assertEqual(Post.objects.get(id=post_id).group.id,
                         post_data['group'])
