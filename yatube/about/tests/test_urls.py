from django.test import TestCase, Client


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_authorpage(self):
        response = guest_client.get('about/author.html')
        self.assertEqual(response.status_code, 200)

    def test_techpage(self):
        response = guest_client.get('about/tech.html')
        self.assertEqual(response.status_code, 200)