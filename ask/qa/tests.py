from django.test import TestCase
from django.urls import resolve
from django.http import HttpRequest

from qa.views import test


class HomePageTest(TestCase):
    '''тест домашней страницы'''

    def test_root_url_resolves_to_home_page_view(self):
        found = resolve('/')
        self.assertEqual(found.func, test)

    def test_test_page_returns_correct_html(self):
        request = HttpRequest()
        response = test(request)
        html = response.content.decode('utf8')
        self.assertIn('OK', html)


class LoginPageTest(TestCase):
    '''тест страницы авторизации'''

    def test_login_url_resolves_to_page_view(self):
        found = resolve('/login/')
        self.assertEqual(found.func, test)


class SignupPageTest(TestCase):
    '''тест страницы регистрации'''

    def test_signup_url_resolves_to_page_view(self):
        found = resolve('/signup/')
        self.assertEqual(found.func, test)


class QuestionPageTest(TestCase):
    '''тест страницы вопроса'''

    def test_question_url_resolves_to_page_view(self):
        found = resolve('/question/123/')
        self.assertEqual(found.func, test)


class AskPageTest(TestCase):
    '''тест страницы добавления вопроса'''

    def test_ask_url_resolves_to_page_view(self):
        found = resolve('/ask/')
        self.assertEqual(found.func, test)


class PopularPageTest(TestCase):
    '''тест страницы с популярными вопросами'''

    def test_popular_url_resolves_to_page_view(self):
        found = resolve('/login/')
        self.assertEqual(found.func, test)


class NewPageTest(TestCase):
    '''тест страницы с новыми вопросами'''

    def test_new_url_resolves_to_page_view(self):
        found = resolve('/login/')
        self.assertEqual(found.func, test)

    def test_test_page_returns_correct_html(self):
        request = HttpRequest()
        response = test(request)
        html = response.content.decode('utf8')
        self.assertIn('OK', html)
