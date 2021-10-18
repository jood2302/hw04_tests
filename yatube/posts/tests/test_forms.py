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
        cls.form_data = {
            'text': 'Тестовый заголовок',
            'group': 1,
        }

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
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=PostFormTest.form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(Post.objects.get(
            id=PostFormTest.post.id).text,
            PostFormTest.post.text)
        self.assertEqual(self.group, PostFormTest.post.group)
        self.assertEqual(self.post.author, PostFormTest.post.author)
        self.assertEqual(response.status_code, 200)

    def test_edit_post(self):
        PostFormTest.post.refresh_from_db()
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={
                'post_id': PostFormTest.post.pk}),
            data=PostFormTest.form_data,
            follow=True
        )
        self.assertTrue(
            Post.objects.filter(
                text=PostFormTest.form_data['text']
            ).exists()
        )
        PostFormTest.post.refresh_from_db()
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

    def test_anonim_client_create_post(self):
        post_count = Post.objects.count()
        response = self.client.post(
            reverse('posts:post_create'),
            data=PostFormTest.form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count)
        self.assertRedirects(
            response, reverse('users:login') + '?next=' + reverse(
                'posts:post_create'
            )
        )
        self.assertEqual(Post.objects.count(), post_count)


"""Если выше это не тест создания поста от анонимного пользователя,
тогда я не очень понимаю что это за условие.В задание написнао так:

Тестирование Forms: «Unittest в Django: тестирование Forms»
В проекте Yatube напишите тесты, которые проверяют, что

-при отправке валидной формы со страницы создания поста
reverse('posts:create_post') создаётся новая запись в базе данных;

-при отправке валидной формы со страницы редактирования поста
reverse('posts:post_edit', args=('post_id',)) происходит
изменение поста с post_id в базе данных.
"""
