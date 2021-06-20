from django.test import TestCase
from django.urls import resolve
from django.http import HttpRequest

from qa.views import test

from qa.models import Question, Answer
from django.contrib.auth.models import User


class QuestionModelTest(TestCase):

    def test_defaul_title_label(self):
        q = Question()
        self.assertEqual(q.title, "")

    def test_defaul_text_label(self):
        q = Question()
        self.assertEqual(q.text, "")

    def test_defaul_added_at_label(self):
        q = Question()
        self.assertEqual(q.added_at, None)

    def test_defaul_rating_label(self):
        q = Question()
        self.assertEqual(q.rating, 0)

    def test_default_author_label(self):
        q = Question()
        self.assertEqual(q.author, None)

    def test_question_can_have_author(self):
        Question(author=User())  # should not raise

    def test_default_likes_label(self):
        q = Question.objects.create()
        q_in_db = Question.objects.get(id=q.id)
        self.assertFalse(q_in_db.likes.all().exists())

    def test_can_add_like_to_question(self):
        q = Question.objects.create()
        user = User.objects.create(email='a@b.com')
        q.likes.add(user)
        q_in_db = Question.objects.get(id=q.id)
        self.assertIn(user, q_in_db.likes.all())

    def test_on_delete(self):
        user = User.objects.create(email='a@b.com')
        q = Question.objects.create(author=user)
        q_in_db = Question.objects.get(id=q.id)
        print(q_in_db)
        self.assertEqual(q_in_db.author, user)
        # User.objects.get(id=user.id).delete()
        # self.assertEqual(q_in_db.author, None)

    def test_question_manager_method_new(self):
        q1 = Question.objects.create(added_at='2021-05-12')
        q2 = Question.objects.create(added_at='2021-02-13')
        q3 = Question.objects.create(added_at='2021-01-09')
        self.assertEqual(
            list(Question.objects.new().all()),
            [q1, q2, q3]
        )

    def test_question_manager_method_popular(self):
        q1 = Question.objects.create(rating=5)
        q2 = Question.objects.create(rating=6)
        q3 = Question.objects.create(rating=7)
        self.assertEqual(
            list(Question.objects.popular().all()),
            [q3, q2, q1]
        )


class AnswerModelTest(TestCase):

    def test_defaul_text_label(self):
        a = Answer()
        self.assertEqual(a.text, "")

    def test_defaul_added_at_label(self):
        a = Answer()
        self.assertEqual(a.added_at, None)

    def test_answer_is_related_to_question(self):
        q = Question.objects.create()
        a = Answer()
        a.question = q
        a.save()
        self.assertIn(a, q.answer_set.all())

    def test_on_delete_cascade(self):
        question = Question.objects.create()
        answer = Answer()
        answer.question = question
        answer.save()
        question.delete()
        self.assertFalse(Answer.objects.filter(pk=answer.id).exists())

    def test_default_author_label(self):
        a = Answer()
        self.assertEqual(a.author, None)

    def test_answer_can_have_author(self):
        Answer(author=User())  # should not raise


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
