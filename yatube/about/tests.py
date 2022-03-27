from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.templates_urls = {
            'urls': {
                '/about/author/': 'about/author.html',
                '/about/tech/': 'about/tech.html'
            },
            'namespace': {
                'about:author': 'about/author.html',
                'about:tech': 'about/tech.html'
            }
        }

    def test_about_urls_exists_at_desired_location(self):
        """Проверка доступности адресов /about/."""
        for address in self.templates_urls['urls'].keys():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_urls_uses_correct_templates(self):
        """Проверка шаблонов для адресов /about/author/, /about/tech/."""
        for address, template in self.templates_urls['urls'].items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_about_pages_accessible_by_name(self):
        """URLs, генерируемые при помощи имён
        about:author и about:tech, доступны.
        """
        for address in self.templates_urls['namespace'].keys():
            with self.subTest(address=address):
                response = self.guest_client.get(reverse(address))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_page_uses_correct_template(self):
        """При запросе к about:author, about:tech
        применяются шаблоны 'about/author.html', 'about/tech.html'."""
        for address, template in self.templates_urls['namespace'].items():
            with self.subTest(address=address):
                response = self.guest_client.get(reverse(address))
                self.assertTemplateUsed(response, template)
