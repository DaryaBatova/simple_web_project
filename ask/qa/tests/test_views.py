from django.test import TestCase

from qa.models import Question, Answer
from qa.views import *
from django.contrib.auth.models import User
from django.urls import reverse, resolve

from datetime import date, timedelta


class QuestionListNewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        #Create 13 questions for pagination tests
        number_of_questions = 13
        user = User.objects.create(username='test', password='test')
        for question_num in range(number_of_questions):
            Question.objects.create(
                title='Question ' + str(question_num),
                text='text ' + str(question_num),
                author=user,
                added_at=date(2021, 5, 1)+timedelta(days=question_num),
                rating=question_num
            )

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse('new_questions'))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        resp = self.client.get(reverse('new_questions'))
        self.assertEqual(resp.status_code, 200)

        self.assertTemplateUsed(resp, 'questions_new.html')

    def test_root_url_resolves_to_question_new_page_view(self):
        found = resolve('/')
        self.assertEqual(found.func, question_list_new)

    def test_attributes_of_paginator(self):
        resp = self.client.get(reverse('new_questions'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('paginator' in resp.context)
        # self.assertTrue('page' in resp.context)
        self.assertTrue(hasattr(resp.context['paginator'], 'count'))
        self.assertTrue(hasattr(resp.context['paginator'], 'num_pages'))
        self.assertTrue(hasattr(resp.context['paginator'], 'page_range'))
        self.assertTrue(resp.context['paginator'].count == 13)
        self.assertTrue(resp.context['paginator'].num_pages == 2)
        self.assertEqual(list(resp.context['paginator'].page_range), [1, 2])

    def test_lists_all_questions(self):
        # Get second page and confirm it has (exactly) remaining 3 items
        resp = self.client.get(reverse('new_questions')+'?page=2')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('page' in resp.context)
        self.assertTrue(hasattr(resp.context['page'], 'object_list'))
        self.assertTrue(len(resp.context['page'].object_list) == 3)

    def test_page_returns_correct_html(self):
        resp = self.client.get(reverse('new_questions')+'?page=2')
        html = resp.content.decode('utf8')
        self.assertIn('Question 0', html)
        self.assertIn('Question 1', html)
        self.assertIn('Question 2', html)
        self.assertNotIn('Question 3', html)


class QuestionListPopularTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        #Create 13 questions for pagination tests
        number_of_questions = 13
        user = User.objects.create(username='test', password='test')
        for question_num in range(number_of_questions):
            Question.objects.create(
                title='Question ' + str(question_num),
                text='text ' + str(question_num),
                author=user,
                rating=question_num
            )

    def test_popular_url_resolves_to_page_view(self):
        found = resolve('/popular/')
        self.assertEqual(found.func, question_list_popular)

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get('/popular/')
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse('popular'))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        resp = self.client.get(reverse('popular'))
        self.assertEqual(resp.status_code, 200)

        self.assertTemplateUsed(resp, 'questions_new.html')

    def test_page_returns_correct_html(self):
        resp = self.client.get(reverse('popular')+'?page=2')
        html = resp.content.decode('utf8')
        self.assertIn('Question 0', html)
        self.assertIn('Question 1', html)
        self.assertIn('Question 2', html)
        self.assertNotIn('Question 3', html)


class QuestionViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        #Create 2 questions for tests
        number_of_questions = 2
        user = User.objects.create(username='test', password='test')
        for question_num in range(number_of_questions):
            Question.objects.create(
                title='Question ' + str(question_num),
                text='text ' + str(question_num),
                author=user,
                rating=question_num
            )

    def test_question_url_resolves_to_page_view(self):
        found = resolve('/question/1/')
        self.assertEqual(found.func, question_view)

    def test_view_url_existing_questions(self):
        self.assertTrue(Question.objects.filter(pk=1).exists())
        resp = self.client.get('/question/'+'1/')
        self.assertTrue(Question.objects.filter(pk=2).exists())
        self.assertEqual(resp.status_code, 200)
        resp = self.client.get('/question/'+'2/')
        self.assertEqual(resp.status_code, 200)

        self.assertTemplateUsed(resp, 'question.html')

    def test_view_existing_questions_accessible_by_name(self):
        # resp = self.client.head(reverse('question', kwargs={'id': 1}))
        # self.assertTrue(resp.request['Location'])
        resp = self.client.get(reverse('question', kwargs={'id': 1}))
        self.assertEqual(resp.status_code, 200)
        resp = self.client.get(reverse('question', kwargs={'id': 2}))
        self.assertEqual(resp.status_code, 200)

    def test_view_non_existen_question(self):
        self.assertFalse(Question.objects.filter(pk=3).exists())
        resp = self.client.get(reverse('question', kwargs={'id': 3}))
        self.assertEqual(resp.status_code, 404)

    def test_page_returns_correct_html(self):
        # Create 3 answers for existing question
        q = Question.objects.get(pk=1)
        for answer_num in range(3):
            Answer.objects.create(
                text='Answer ' + str(answer_num),
                question=q,
                author=q.author
            )
        resp = self.client.get(reverse('question', kwargs={'id': 1}))
        html = resp.content.decode('utf8')
        self.assertIn('Question 0', html)
        self.assertIn('text 0', html)
        self.assertIn('Answer 0', html)
        self.assertIn('Answer 1', html)
        self.assertIn('Answer 2', html)


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


class AskPageTest(TestCase):
    '''тест страницы добавления вопроса'''

    def test_ask_url_resolves_to_page_view(self):
        found = resolve('/ask/')
        self.assertEqual(found.func, test)
