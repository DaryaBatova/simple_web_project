import unittest
from unittest.mock import patch, Mock
from datetime import date, timedelta
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse, resolve
from django.utils.html import escape

from qa.models import Question, Answer, QuestionLikes
from qa.views import *
from qa.forms import (
    EMPTY_TITLE_ERROR, EMPTY_TEXT_ERROR, AskForm, AnswerForm,
    EMPTY_USERNAME_ERROR, EMPTY_EMAIL_ERROR, EMPTY_PASSWORD_ERROR, SignupForm, LoginForm
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
        # Create test user
        cls.test_user = User.objects.create(email='a@b.com')

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

    def test_page_with_a_nonexistent_question_returns_404_error(self):
        self.assertFalse(Question.objects.filter(pk=3).exists())
        resp = self.client.get(reverse('question', kwargs={'id': 3}))
        self.assertEqual(resp.status_code, 404)

    def test_page_with_an_existing_question_returns_correct_html(self):
        # Create 3 answers for existing question
        q = Question.objects.get(pk=1)
        for answer_num in range(3):
            Answer.objects.create(
                text='Answer ' + str(answer_num),
                question=q,
                author=q.author
            )
        resp = self.client.get(q.get_absolute_url())
        self.assertContains(resp, escape('Question 0'))
        self.assertContains(resp, escape('text 0'))
        self.assertContains(resp, escape('Answer 0'))
        self.assertContains(resp, escape('Answer 1'))
        self.assertContains(resp, escape('Answer 2'))

    def test_page_with_an_existing_question_uses_answer_form(self):
        response = self.client.get(reverse('question', kwargs={'id': 1}))
        self.assertIsInstance(response.context['form'], AnswerForm)

    def test_the_data_is_correctly_passed_to_the_form_context(self):
        # log in
        self.client.force_login(self.test_user)
        question = Question.objects.get(pk=1)
        response = self.client.get(f'/question/{question.id}/')
        self.assertEqual(response.context['question'], question)
        self.assertFalse(response.context['answers'])
        self.assertEqual(response.context['user'], self.test_user)

    def test_can_save_a_POST_request_to_an_existing_question_if_user_is_authenticated(self):
        # log in
        self.client.force_login(self.test_user)
        question = Question.objects.get(pk=1)
        self.client.post(f'/question/{question.id}/', data={'text': 'A new answer for an existing question'})
        self.assertEqual(Answer.objects.count(), 1)

    def test_for_invalid_input_doesnt_save_but_shows_errors(self):
        post_data = {'text': ''}
        response = self.client.post(reverse('question', kwargs={'id': 1}), data=post_data)
        self.assertEqual(Answer.objects.count(), 0)
        # self.assertContains(response, escape(EMPTY_TEXT_ERROR))

    def test_answer_author_is_saved_if_user_is_authenticated(self):
        self.client.force_login(self.test_user)
        self.client.post(reverse('question', kwargs={'id': 1}), data={'text': 'new answer'})
        new_answer = Answer.objects.first()
        question = Question.objects.get(pk=1)
        self.assertEqual(new_answer.text, 'new answer')
        self.assertEqual(new_answer.question, question)
        self.assertEqual(new_answer.author, self.test_user)

    def test_redirects_to_form_returned_object_if_form_valid_and_user_is_authenticated(self):
        # log in
        self.client.force_login(self.test_user)
        question = Question.objects.get(pk=1)
        post_data = {'text': 'A new answer'}
        response = self.client.post(reverse('question', kwargs={'id': 1}), data=post_data)
        new_answer = Answer.objects.first()
        self.assertEqual(new_answer.question, question)
        self.assertRedirects(response, f'/question/{new_answer.question.id}/')

    def test_new_answer_display_on_question_page_after_redirect(self):
        # log in
        self.client.force_login(self.test_user)
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
        response = self.client.post(reverse('question', kwargs={'id': 1}), data=post_data)
        self.assertEqual(response.url, '/question/1/')

        response = self.client.get(response.url)
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

    def test_redirects_to_login_if_form_valid_but_user_isnt_authenticated(self):
        post_data = {'title': 'Question 1', 'text': 'A new question'}
        response = self.client.post(reverse('question', kwargs={'id': 1}), data=post_data)
        self.assertRedirects(response, reverse('login'))
        self.assertTemplateNotUsed(response, 'question.html')


class LoginPageTest(TestCase):
    """Login page test"""

    @classmethod
    def setUpTestData(cls):
        # Create 1 user for tests
        from django.contrib.auth.hashers import make_password
        password = make_password('12a3W@mя45')
        User.objects.create(username='test-user', email='a@b.com', password=password)

    def test_login_url_resolves_to_page_view(self):
        found = resolve('/login/')
        self.assertEqual(found.func, login_view)

    def test_login_page_uses_template_login(self):
        response = self.client.get(reverse('login'))
        self.assertTemplateUsed(response, 'login_form.html')

    def test_login_page_uses_login_form(self):
        response = self.client.get(reverse('login'))
        self.assertIsInstance(response.context['form'], LoginForm)

    def test_can_save_a_POST_request(self):
        from django.contrib.auth import authenticate
        user = authenticate(username='test-user', password='12a3W@mя45')
        self.assertIsNotNone(user)

        post_data = {'username': 'test-user', 'password': '12a3W@mя45'}
        response = self.client.post(reverse('login'), data=post_data)
        self.assertTemplateNotUsed(response, 'login_form.html')

    def test_before_login_the_session_isnt_created(self):
        response = self.client.get(reverse('login'))
        self.assertIsNone(response.context['session'].session_key)
        self.assertNotIsInstance(response.context['user'], User)

    def test_after_login_the_session_is_created(self):
        user = User.objects.first()
        post_data = {'username': 'test-user', 'password': '12a3W@mя45'}
        self.client.post(reverse('login'), data=post_data)
        # after login
        response = self.client.get(reverse('login'))
        self.assertIsNotNone(response.context['session'].session_key)
        self.assertEqual(response.context['user'], user)

        # TODO add session in popular view
        new_response = self.client.get(reverse('popular'))
        # self.assertIsNotNone(new_response.context['session'].session_key)
        # self.assertEqual(response.context['session'].session_key, new_response.context['session'].session_key)

    def test_for_invalid_input_shows_errors(self):
        post_data = {'username': '', 'password': ''}
        response = self.client.post(reverse('login'), data=post_data)
        self.assertContains(response, escape(EMPTY_USERNAME_ERROR))
        self.assertContains(response, escape(EMPTY_PASSWORD_ERROR))

    def test_redirects_to_page_with_new_questions_if_form_valid(self):
        post_data = {'username': 'test-user', 'password': '12a3W@mя45'}
        response = self.client.post(reverse('login'), data=post_data)
        self.assertRedirects(response, reverse('new_questions'))

    def test_renders_template_with_form_if_form_invalid(self):
        post_data = {'username': '', 'password': ''}
        response = self.client.post(reverse('login'), data=post_data)
        self.assertTemplateUsed(response, 'login_form.html')


class LogoutTest(TestCase):

    def test_logout_url_resolves_to_page_view(self):
        found = resolve('/logout/')
        self.assertEqual(found.func, logout_view)

    def test_user_can_logout_and_redirects_to_page_with_new_questions(self):
        user = User.objects.create(email='a@b.com')
        # is_authenticated this attribute is True for any User instance
        self.assertTrue(user.is_authenticated)
        self.client.force_login(user)
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('new_questions'))


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
        response = self.client.get(reverse('ask'))
        self.assertTemplateUsed(response, 'ask_form.html')

    def test_ask_page_uses_ask_form(self):
        response = self.client.get(reverse('ask'))
        self.assertIsInstance(response.context['form'], AskForm)

    def test_can_save_a_POST_request_if_user_is_authenticated(self):
        # log in
        user = User.objects.create(email='a@b.com')
        self.client.force_login(user)

        # post request
        post_data = {'title': 'Question 1', 'text': 'A new question'}
        self.client.post(reverse('ask'), data=post_data)
        self.assertEqual(Question.objects.count(), 1)
        new_question = Question.objects.first()
        self.assertEqual(new_question.title, 'Question 1')
        self.assertEqual(new_question.text, 'A new question')

    def test_for_invalid_input_doesnt_save_question_but_shows_errors(self):
        post_data = {'title': '', 'text': ''}
        response = self.client.post(reverse('ask'), data=post_data)
        self.assertEqual(Question.objects.count(), 0)
        self.assertContains(response, escape(EMPTY_TITLE_ERROR))
        self.assertContains(response, escape(EMPTY_TEXT_ERROR))

    def test_question_author_is_saved_if_user_is_authenticated(self):
        user = User.objects.create(email='a@b.com')
        self.client.force_login(user)
        self.client.post(reverse('ask'), data={'title': 'Question', 'text': 'new question'})
        new_question = Question.objects.first()
        self.assertEqual(new_question.author, user)

    def test_redirects_to_form_returned_object_if_form_valid(self):
        user = User.objects.create(email='a@b.com')
        self.client.force_login(user)
        post_data = {'title': 'Question 1', 'text': 'A new question'}
        response = self.client.post(reverse('ask'), data=post_data)
        new_question = Question.objects.first()
        self.assertRedirects(response, f'/question/{new_question.id}/')

    def test_renders_template_with_form_if_form_invalid(self):
        post_data = {'title': '', 'text': ''}
        response = self.client.post(reverse('ask'), data=post_data)
        self.assertTemplateUsed(response, 'ask_form.html')

    def test_redirects_to_login_if_form_valid_but_user_isnt_authenticated(self):
        post_data = {'title': 'Question 1', 'text': 'A new question'}
        response = self.client.post(reverse('ask'), data=post_data)
        self.assertRedirects(response, reverse('login'))
        self.assertTemplateNotUsed(response, 'ask_form.html')

    def test_doesnt_redirect_on_GET_request_and_session_key_is_none_if_user_isnt_authenticated(self):
        response = self.client.get(reverse('ask'))
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context['session'].session_key)
        # self.assertIsNone(self.client.session.session_key)

    def test_doesnt_redirect_on_GET_request_and_session_key_isnt_none_if_user_is_authenticated(self):
        user = User.objects.create(email='a@b.com')
        self.client.force_login(user)
        response = self.client.get(reverse('ask'))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['session'].session_key)
        # self.assertIsNotNone(self.client.session.session_key)

    def test_the_session_is_saved_if_the_form_is_invalid_but_user_is_authenticated(self):
        user = User.objects.create(email='a@b.com')
        self.client.force_login(user)
        response = self.client.get(reverse('ask'))
        self.assertIsNotNone(response.context['session'].session_key)
        # bad post data
        post_data = {'title': '', 'text': ''}
        new_response = self.client.post(reverse('ask'), data=post_data)
        self.assertIsNotNone(new_response.context['session'].session_key)
        self.assertEqual(response.context['session'].session_key, new_response.context['session'].session_key)


class AddLikeViewTest(TestCase):

    def setUp(self):
        # create two questions
        self.q1 = Question.objects.create(title='Question 1', text='It is a question 1', rating=2)
        self.q2 = Question.objects.create(title='Question 2', text='It is a question 2', rating=-1)

        # create two users
        self.joe = User.objects.create(username='joe')
        self.jim = User.objects.create(username='jim')

        # let joe rate both questions
        QuestionLikes.objects.create(question=self.q1, user=self.joe, is_liked=True)
        QuestionLikes.objects.create(question=self.q2, user=self.joe, is_liked=False)

        # let jim rate the first question
        QuestionLikes.objects.create(question=self.q1, user=self.jim, is_liked=True)

    def test_the_user_can_rate_the_question_for_the_first_time(self):
        # Can Jim rate the second question?
        self.assertFalse(self.q2 in Question.objects.filter(likes=self.jim))
        self.client.force_login(self.jim)
        post_data = {'question_id': self.q2.id, 'operation': 'Like'}
        response = self.client.post(reverse('like'), data=post_data)
        # After sending the request, was Jim added to the list of users who liked the second question?
        self.assertTrue(self.q2 in Question.objects.filter(likes=self.jim))
        row = QuestionLikes.objects.get(question=self.q2, user=self.jim)
        self.assertTrue(row.is_liked)

    def test_the_user_can_like_the_question_by_raising_its_rating(self):
        # if the user rates the question for the first time, then the rating of the question changes by 1 unit (+/-1)
        self.assertEqual(self.q2.rating, -1)

        self.client.force_login(self.jim)
        post_data = {'question_id': self.q2.id, 'operation': 'Like'}
        self.client.post(reverse('like'), data=post_data)

        q2 = Question.objects.get(pk=2)
        self.assertEqual(q2.rating, 0)

    def test_the_user_first_disliked_and_then_liked_the_rating_increased_by_2(self):
        self.assertTrue(self.q2 in Question.objects.filter(likes=self.joe))
        row = QuestionLikes.objects.get(question=self.q2, user=self.joe)
        self.assertFalse(row.is_liked)

        self.assertEqual(self.q2.rating, -1)

        self.client.force_login(self.joe)
        post_data = {'question_id': self.q2.id, 'operation': 'Like'}
        self.client.post(reverse('like'), data=post_data)

        q2 = Question.objects.get(pk=2)
        self.assertEqual(q2.rating, 1)

    def test_the_user_first_liked_and_then_disliked_the_rating_decreased_by_2(self):
        self.assertTrue(self.q1 in Question.objects.filter(likes=self.joe))
        row = QuestionLikes.objects.get(question=self.q1, user=self.joe)
        self.assertTrue(row.is_liked)

        self.assertEqual(self.q1.rating, 2)

        self.client.force_login(self.joe)
        post_data = {'question_id': self.q1.id, 'operation': 'Dislike'}
        self.client.post(reverse('like'), data=post_data)

        q1 = Question.objects.get(pk=1)
        self.assertEqual(q1.rating, 0)

    def test_the_user_first_disliked_and_then_disliked_the_rating_increased_by_1(self):
        self.assertTrue(self.q2 in Question.objects.filter(likes=self.joe))
        row = QuestionLikes.objects.get(question=self.q2, user=self.joe)
        self.assertFalse(row.is_liked)

        self.assertEqual(self.q2.rating, -1)

        self.client.force_login(self.joe)
        post_data = {'question_id': self.q2.id, 'operation': 'Dislike'}
        self.client.post(reverse('like'), data=post_data)

        q2 = Question.objects.get(pk=2)
        self.assertEqual(q2.rating, 0)

    def test_the_user_first_liked_and_then_liked_the_rating_decreased_by_1(self):
        self.assertTrue(self.q1 in Question.objects.filter(likes=self.joe))
        row = QuestionLikes.objects.get(question=self.q1, user=self.joe)
        self.assertTrue(row.is_liked)

        self.assertEqual(self.q1.rating, 2)

        self.client.force_login(self.joe)
        post_data = {'question_id': self.q1.id, 'operation': 'Like'}
        self.client.post(reverse('like'), data=post_data)

        q1 = Question.objects.get(pk=1)
        self.assertEqual(q1.rating, 1)


class DeleteAnswerViewTest(TestCase):

    def setUp(self):
        # create two users
        self.joe = User.objects.create(username='joe')
        self.bob = User.objects.create(username='bob')
        # create question
        self.q1 = Question.objects.create(title='Question 1', text='New question', author=self.joe)
        # create two answers
        self.a1 = Answer.objects.create(text="It's Joe answer", question=self.q1, author=self.joe)
        self.a2 = Answer.objects.create(text="It's Bob answer", question=self.q1, author=self.bob)

    def test_joe_can_delete_his_answer(self):
        self.client.force_login(self.joe)
        self.assertEqual(Answer.objects.count(), 2)
        response = self.client.post(reverse('delete_answer'), {'answer_id': self.a1.pk})
        self.assertEqual(Answer.objects.count(), 1)
        self.assertFalse(Answer.objects.filter(author=self.joe).exists())

    def test_after_deleting_the_answer_is_not_displayed(self):
        self.client.force_login(self.joe)
        response = self.client.get(reverse('question', kwargs={'id': self.q1.pk}))
        self.assertContains(response, escape("It's Joe answer"))
        self.assertContains(response, escape("It's Bob answer"))
        response = self.client.post(reverse('delete_answer'), {'answer_id': self.a1.pk})
        new_response = self.client.get(response.url)
        self.assertNotContains(new_response, escape("It's Joe answer"))
        self.assertContains(new_response, escape("It's Bob answer"))

    def test_joe_cannt_delete_bobs_answer(self):
        self.client.force_login(self.joe)
        self.assertEqual(Answer.objects.count(), 2)
        response = self.client.post(reverse('delete_answer'), {'answer_id': self.a2.pk})
        self.assertEqual(Answer.objects.count(), 2)
        self.assertTrue(Answer.objects.filter(author=self.bob).exists())
        