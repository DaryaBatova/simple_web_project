import unittest
from unittest.mock import patch, Mock
from datetime import date, timedelta
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse, resolve
from django.utils.html import escape

from qa.models import Question, Answer
from qa.views import *
from qa.forms import (
    EMPTY_TITLE_ERROR, EMPTY_TEXT_ERROR, AskForm, AnswerForm,
    EMPTY_USERNAME_ERROR, EMPTY_EMAIL_ERROR, EMPTY_PASSWORD_ERROR, SignupForm
)


class QuestionListNewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create 13 questions for pagination tests
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
        self.assertContains(resp, escape('Question 0'))
        self.assertContains(resp, escape('Question 1'))
        self.assertContains(resp, escape('Question 2'))
        self.assertNotContains(resp, escape('Question 3'))


class QuestionListPopularTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create 13 questions for pagination tests
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
        self.assertContains(resp, escape('Question 0'))
        self.assertContains(resp, escape('Question 1'))
        self.assertContains(resp, escape('Question 2'))
        self.assertNotContains(resp, escape('Question 3'))


class QuestionViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create 2 questions for tests
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
        resp = self.client.get(reverse('question', kwargs={'id': 1}))
        self.assertEqual(resp.status_code, 200)
        resp = self.client.get(reverse('question', kwargs={'id': 2}))
        self.assertEqual(resp.status_code, 200)

    def test_view_nonexistent_question(self):
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
        self.assertContains(resp, escape('Question 0'))
        self.assertContains(resp, escape('text 0'))
        self.assertContains(resp, escape('Answer 0'))
        self.assertContains(resp, escape('Answer 1'))
        self.assertContains(resp, escape('Answer 2'))

    def test_question_page_uses_answer_form(self):
        response = self.client.get(reverse('question', kwargs={'id': 1}))
        self.assertIsInstance(response.context['form'], AnswerForm)

    def test_can_save_a_POST_request_to_an_existing_question(self):
        question = Question.objects.get(pk=1)
        response = self.client.get(f'/question/{question.id}/')
        self.assertEqual(response.context['question'], question)
        self.assertFalse(response.context['answers'])

        response = self.client.post(
            f'/question/{question.id}/',
            data={'text': 'A new answer for an existing question'}
        )
        self.assertEqual(Answer.objects.count(), 1)
        new_answer = Answer.objects.first()
        self.assertEqual(new_answer.text, 'A new answer for an existing question')
        self.assertEqual(new_answer.question, question)
        self.assertEqual(new_answer.author, None)

    def test_for_invalid_input_doesnt_save_but_shows_errors(self):
        post_data = {'text': ''}
        response = self.client.post(reverse('question', kwargs={'id': 1}), data=post_data)
        self.assertEqual(Answer.objects.count(), 0)
        self.assertContains(response, escape(EMPTY_TEXT_ERROR))

    def test_answer_author_is_saved_if_user_is_authenticated(self):
        # TODO fix this method
        user = User.objects.create(email='a@b.com')
        self.client.force_login(user)
        self.client.post(reverse('question', kwargs={'id': 1}), data={'text': 'new answer'})
        new_answer = Answer.objects.first()
        # author is None for now
        self.assertEqual(new_answer.author, user.id)

    def test_redirects_to_form_returned_object_if_form_valid(self):
        question = Question.objects.get(pk=1)
        post_data = {'text': 'A new answer'}
        response = self.client.post(reverse('question', kwargs={'id': 1}), data=post_data)
        new_answer = Answer.objects.first()
        self.assertEqual(new_answer.question, question)
        self.assertRedirects(response, f'/question/{new_answer.question.id}/')

    def test_new_answer_display_on_question_page_after_redirect(self):
        question = Question.objects.get(pk=1)
        for answer_num in range(2):
            Answer.objects.create(
                text='Answer ' + str(answer_num),
                question=question,
                author=question.author
            )
        response = self.client.get(reverse('question', kwargs={'id': 1}))
        self.assertContains(response, escape('Question 0'))
        self.assertContains(response, escape('text 0'))
        self.assertContains(response, escape('Answer 0'))
        self.assertContains(response, escape('Answer 1'))

        post_data = {'text': 'A new answer'}
        self.client.post(reverse('question', kwargs={'id': 1}), data=post_data)
        new_answer = Answer.objects.first()
        response = self.client.get(f'/question/{new_answer.question.id}/')
        self.assertContains(response, escape('Question 0'))
        self.assertContains(response, escape('text 0'))
        self.assertContains(response, escape('Answer 0'))
        self.assertContains(response, escape('Answer 1'))
        # new answer displayed
        self.assertContains(response, escape('A new answer'))

    def test_renders_template_with_form_if_form_invalid(self):
        post_data = {'text': ''}
        response = self.client.post(reverse('question', kwargs={'id': 1}), data=post_data)
        self.assertTemplateUsed(response, 'question.html')


class LoginPageTest(TestCase):
    """Login page test"""

    def test_login_url_resolves_to_page_view(self):
        found = resolve('/login/')
        self.assertEqual(found.func, test)


class SignupPageTest(TestCase):
    """Registration page test"""

    def test_signup_url_resolves_to_page_view(self):
        found = resolve('/signup/')
        self.assertEqual(found.func, signup)

    def test_signup_page_uses_template_signup(self):
        response = self.client.get(reverse('signup'))
        self.assertTemplateUsed(response, 'signup_form.html')

    def test_signup_page_uses_signup_form(self):
        response = self.client.get(reverse('signup'))
        self.assertIsInstance(response.context['form'], SignupForm)

    def test_can_save_a_POST_request(self):
        post_data = {'username': 'test-user', 'email': 'a@b.com', 'password': '12a3W@mя45'}
        self.client.post(reverse('signup'), data=post_data)
        self.assertEqual(User.objects.count(), 1)
        new_user = User.objects.first()
        self.assertEqual(new_user.username, 'test-user')
        self.assertEqual(new_user.email, 'a@b.com')

    def test_for_invalid_input_doesnt_save_but_shows_errors(self):
        post_data = {'username': '', 'email': '', 'password': ''}
        response = self.client.post(reverse('signup'), data=post_data)
        self.assertEqual(User.objects.count(), 0)
        self.assertContains(response, escape(EMPTY_USERNAME_ERROR))
        self.assertContains(response, escape(EMPTY_EMAIL_ERROR))
        self.assertContains(response, escape(EMPTY_PASSWORD_ERROR))

    def test_redirects_to_page_with_new_questions_if_form_valid(self):
        post_data = {'username': 'test-user', 'email': 'a@b.com', 'password': '12a3W@mя45'}
        response = self.client.post(reverse('signup'), data=post_data)
        self.assertRedirects(response, reverse('new_questions'))

    def test_renders_template_with_form_if_form_invalid(self):
        post_data = {'username': '', 'email': '', 'password': ''}
        response = self.client.post(reverse('signup'), data=post_data)
        self.assertTemplateUsed(response, 'signup_form.html')


class AddQuestionViewTest(TestCase):
    """Ask page test"""

    def test_uses_ask_form_template(self):
        response = self.client.get('/ask/')
        self.assertTemplateUsed(response, 'ask_form.html')

    def test_ask_page_uses_ask_form(self):
        response = self.client.get('/ask/')
        self.assertIsInstance(response.context['form'], AskForm)

    def test_can_save_a_POST_request(self):
        post_data = {'title': 'Question 1', 'text': 'A new question'}
        self.client.post('/ask/', data=post_data)
        self.assertEqual(Question.objects.count(), 1)
        new_question = Question.objects.first()
        self.assertEqual(new_question.title, 'Question 1')
        self.assertEqual(new_question.text, 'A new question')
        self.assertEqual(new_question.author, None)

    def test_for_invalid_input_doesnt_save_but_shows_errors(self):
        post_data = {'title': '', 'text': ''}
        response = self.client.post('/ask/', data=post_data)
        self.assertEqual(Question.objects.count(), 0)
        self.assertContains(response, escape(EMPTY_TITLE_ERROR))
        self.assertContains(response, escape(EMPTY_TEXT_ERROR))

    def test_question_author_is_saved_if_user_is_authenticated(self):
        # TODO fix this method
        user = User.objects.create(email='a@b.com')
        self.client.force_login(user)
        self.client.post('/ask/', data={'title': 'Question', 'text': 'new question'})
        question_ = Question.objects.first()
        # author is None for now
        self.assertEqual(question_.author, user.id)

    def test_redirects_to_form_returned_object_if_form_valid(self):
        post_data = {'title': 'Question 1', 'text': 'A new question'}
        response = self.client.post('/ask/', data=post_data)
        question_ = Question.objects.first()
        self.assertRedirects(response, f'/question/{question_.id}/')

    def test_renders_template_with_form_if_form_invalid(self):
        post_data = {'title': '', 'text': ''}
        response = self.client.post('/ask/', data=post_data)
        self.assertTemplateUsed(response, 'ask_form.html')
