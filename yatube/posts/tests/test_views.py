from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class TaskPagesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test_user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Тест',
            slug='7897987',
        )
        self.post = Post.objects.create(
            text='Тестовый текст',
            author=self.user,
            group=self.group
        )
        self.form_data = {
            'text': 'formtesttext',
            'group': self.group.id,
        }
        self.new_post = self.authorized_client.post(
            reverse('posts:post_create'),
            data=self.form_data,
            follow=True
        )
        self.public_index_template = 'posts/index.html'
        self.public_group_page_template = 'posts/group_list.html'
        self.private_create_post_template = 'posts/create_post.html'
        self.private_edit_post_template = 'posts/create_post.html'
        self.public_profile = 'posts/profile.html'
        self.public_post = 'posts/post_detail.html'

    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            self.public_index_template: reverse('posts:index'),
            self.public_profile: reverse('posts:profile',
                                         kwargs={'username': 'AntonKarpov'}),
            self.public_post: reverse('posts:post_detail',
                                      kwargs={'post_id': '1'}),
            self.private_edit_post_template: reverse('posts:post_edit',
                                                     kwargs={'post_id':
                                                             '1'}),
            self.private_create_post_template: reverse('posts:post_create'),
            self.public_group_page_template: (
                reverse('posts:group_list', kwargs={'slug': '7897987'})
            ),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertTemplateUsed(response, self.private_create_post_template)

    def test_context(self):
        url_names = [reverse('posts:index'),
                     reverse('posts:post_detail', kwargs={'post_id': '2'}),
                     reverse('posts:post_edit',
                             kwargs={'post_id': '2'}),
                     reverse('posts:group_list',
                             kwargs={'slug': self.group.slug}),
                     reverse('posts:profile',
                             kwargs={'username': self.user.username})]
        for url in url_names:
            response = self.authorized_client.get(url)
            self.assertContains(response, self.form_data['text'])
            self.assertContains(response, self.user)
            self.assertContains(response, self.group.id)

    def test_check_post_in_group(self):
        t_group = Group.objects.create(
            title='Заголовок',
            slug='test',
            description='Текст',
        )
        Group.objects.create(
            title='Заголовок1',
            slug='test1',
            description='Текст1',
        )
        Post.objects.create(
            text='formtesttext',
            author=self.user,
            group=t_group
        )
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test'}))
        self.assertEqual(response.context['group'].title, 'Заголовок')
        self.assertEqual(response.context['group'].slug, 'test')
        self.assertEqual(response.context['group'].description, 'Текст')
        first_object = response.context['page_obj'][0]
        post_text = first_object.text
        post_group = first_object.group
        self.assertEqual(post_text, 'formtesttext')
        self.assertEqual(post_group.title, 'Заголовок')
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test1'})
        )
        self.assertFalse(response.context['page_obj'].has_next())

    def test_chech_post_in_index(self):
        response = self.authorized_client.get(
            reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text = first_object.text
        self.assertEqual(post_text, 'formtesttext')
        first_object = response.context['page_obj'][0]
        post_text = first_object.text
        self.assertFalse(response.context['page_obj'].has_next())

    def test_chech_post_in_profile(self):
        response = self.authorized_client.get(
            reverse('posts:profile'))
        first_object = response.context['page_obj'][0]
        post_text = first_object.text
        self.assertEqual(post_text, 'formtesttext')
        first_object = response.context['page_obj'][0]
        post_text = first_object.text
        self.assertFalse(response.context['page_obj'].has_next())

class PaginatorTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='Test_user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        for i in range(0, 13):
            Post.objects.create(
                text='Тестовый текст',
                author=self.user,)

    def test_first_page_contains_ten_records(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        response = self.authorized_client.get(
            reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_group_list_first_page_contains_ten_records(self):
        response = self.authorized_client.get(reverse('posts:group_list'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_group_list_second_page_contains_three_records(self):
        response = self.authorized_client.get(
            reverse('posts:') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_profile_first_page_contains_ten_records(self):
        response = self.authorized_client.get(reverse('posts:profile'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_profile_second_page_contains_three_records(self):
        response = self.authorized_client.get(
            reverse('posts:profile') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)