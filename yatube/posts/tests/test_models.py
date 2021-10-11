from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Post, Group

User = get_user_model()


class TestGroupModel(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group_title = 'Group_test'
        cls.group = Group.objects.create(
            title=cls.group_title,
            slug='Ntcn',
            description='Тестовый текст.'
        )

    def test_object_name_is_title_group(cls):
        group = Group.objects.all().first()
        expected_object_name = group.title
        cls.assertEqual(expected_object_name, str(cls.group_title),
                        '__str__ работает неверно')


class TestPostModel(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = User.objects.create(username='Test',
                                   last_name='User',
                                   email='test@user.net',
                                   password='Test_User')
        cls.task = Post.objects.create(
            author=user,
            text='Тестовый текст',
        )

    def test_object_text_long(self):
        task = Post.objects.all().first()
        expected_object_name = task.text[:15]
        self.assertEqual(expected_object_name, str(task),
                         'Не проходит по ограничению поста в 15 символов')