from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password

from qa.forms import (
    EMPTY_TITLE_ERROR, EMPTY_TEXT_ERROR, AskForm, AnswerForm,
    EMPTY_USERNAME_ERROR, EMPTY_EMAIL_ERROR, EMPTY_PASSWORD_ERROR, SignupForm, LoginForm
)

from qa.models import Question, Answer


class AskFormTest(TestCase):

    def test_ask_form_title_field_label(self):
        form = AskForm()
        self.assertTrue(form.fields['title'].label == 'Question title')

    def test_ask_form_text_field_label(self):
        form = AskForm()
        self.assertTrue(form.fields['text'].label == 'Question text')

    def test_ask_form_validation_for_blank_title_and_text(self):
        form = AskForm(data={'title': '', 'text': ''})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['title'], [EMPTY_TITLE_ERROR])
        self.assertEqual(form.errors['text'], [EMPTY_TEXT_ERROR])

    def test_ask_form_is_valid(self):
        title = 'Question 1'
        text = 'Form is valid?'
        form_data = {'title': title, 'text': text}
        form = AskForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_ask_form_save_question(self):
        title = 'Question 2'
        text = 'Question will be saved?'
        form_data = {'title': title, 'text': text}
        form = AskForm(data=form_data)
        self.assertTrue(form.is_valid())
        saved_question = form.save()
        self.assertTrue(Question.objects.filter(title='Question 2', text__contains='saved').exists())
        self.assertEqual(Question.objects.count(), 1)
        question = Question.objects.get(title='Question 2', text__contains='saved')
        self.assertEqual(question, saved_question)


class AnswerFormTest(TestCase):

    def test_answer_form_text_field_label(self):
        form = AnswerForm()
        self.assertTrue(form.fields['text'].label == 'Answer text')

    def test_answer_form_question_field(self):
        form = AnswerForm()
        self.assertEqual(form.fields['question'].widget.input_type, 'hidden')

    def test_answer_form_validation_for_blank_text(self):
        form = AnswerForm(data={'text': ''})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['text'], [EMPTY_TEXT_ERROR])

    def test_answer_form_is_valid(self):
        question = Question.objects.create(title='Question')
        question.save()
        form_data = {'text': 'Form is valid?', 'question': question.id}
        form = AnswerForm(form_data)
        self.assertFalse(form.has_error('text'))
        self.assertFalse(form.has_error('question'))
        self.assertEqual(form.errors, {})
        self.assertTrue(form.is_valid())

    def test_answer_form_is_invalid(self):
        # post request to nonexistent question
        self.assertFalse(Question.objects.filter(pk=1).exists())
        form_data = {'text': 'Form is valid?', 'question': 1}
        form = AnswerForm(form_data)
        self.assertFalse(form.has_error('text'))
        self.assertTrue(form.has_error('question'))
        self.assertEqual(form.errors, {'question': ["This question doesn't exist"]})
        self.assertFalse(form.is_valid())

    def test_answer_form_save_answer(self):
        question = Question.objects.create(title='Question')
        question.save()
        text = 'Answer will be saved?'
        form_data = {'text': text, 'question': question.id}
        form = AnswerForm(data=form_data)
        self.assertTrue(form.is_valid())
        saved_answer = form.save()
        self.assertEqual(Answer.objects.count(), 1)
        self.assertTrue(saved_answer in question.answer_set.all())


class SignupFormTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        username = 'test-user'
        email = 'a@b.com'
        cls.form_data = {'username': username, 'email': email}

    def test_signup_form_validation_for_blank_fields(self):
        form = SignupForm(data={'username': '', 'email': '', 'password': ''})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['username'], [EMPTY_USERNAME_ERROR])
        self.assertEqual(form.errors['email'], [EMPTY_EMAIL_ERROR])
        self.assertEqual(form.errors['password'], [EMPTY_PASSWORD_ERROR])

    def test_signup_form_invalid_if_password_with_short_length(self):
        # test method clean_password (MinimumLength validator)
        short_password = '1234567'
        form_data = self.form_data
        form_data['password'] = short_password
        form = SignupForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertTrue('This password is too short' in str(form.errors['password']))

    def test_signup_form_invalid_if_password_is_numeric(self):
        # test method clean_password (NumericPassword validator)
        numeric_password = '12345678'
        form_data = self.form_data
        form_data['password'] = numeric_password
        form = SignupForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertTrue('This password is entirely numeric' in str(form.errors['password']))

    def test_signup_form_invalid_if_password_is_unreliable(self):
        # test method clean_password (own validator)
        unreliable_password = '1234a5678'
        form_data = self.form_data
        form_data['password'] = unreliable_password
        form = SignupForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertTrue('Password is weak' in str(form.errors['password']))

    def test_signup_form_valid_if_password_is_reliable(self):
        # test method clean_password
        reliable_password = '12a3W@mя45'
        form_data = self.form_data
        form_data['password'] = reliable_password
        form = SignupForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_signup_form_save_user_if_form_valid(self):
        # test method save
        reliable_password = '12a3W@mя45'
        form_data = self.form_data
        form_data['password'] = reliable_password
        form = SignupForm(data=form_data)
        self.assertTrue(form.is_valid())

        saved_user = form.save()
        self.assertEqual(User.objects.count(), 1)
        user_in_db = User.objects.first()
        self.assertEqual(saved_user.username, user_in_db.username)
        self.assertEqual(saved_user.email, user_in_db.email)
        self.assertEqual(saved_user.password, user_in_db.password)

    def test_signup_form_wont_save_users_with_the_same_name(self):
        # test method clean_username
        reliable_password = '12a3W@mя45'
        form_data = self.form_data
        form_data['password'] = reliable_password
        form = SignupForm(data=form_data)
        self.assertTrue(form.is_valid())

        saved_user = form.save()
        self.assertEqual(saved_user.username, 'test-user')
        self.assertEqual(User.objects.count(), 1)

        new_form_data = self.form_data
        form = SignupForm(data=new_form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['username'], [f"A user with name {saved_user.username} already exists"])
        self.assertEqual(User.objects.count(), 1)


class LoginFormTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        username = 'test-user'
        password = make_password('12a3W@mя45')
        User.objects.create(username=username, email='a@b.com', password=password)

    def test_login_form_validation_for_blank_fields(self):
        form = LoginForm(data={'username': '', 'password': ''})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['username'], [EMPTY_USERNAME_ERROR])
        self.assertEqual(form.errors['password'], [EMPTY_PASSWORD_ERROR])

    def test_login_form_invalid_if_username_isnt_registered(self):
        # test method clean
        form_data = {'username': 'incorrect', 'password': '12a3W@mя45'}
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'], ["Username or password is incorrect"])

    def test_login_form_invalid_if_password_doesnt_match_the_user(self):
        # test method clean
        numeric_password = '12345678'
        form_data = {'username': 'test-user', 'password': numeric_password}
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'], ["Username or password is incorrect"])

    def test_login_form_valid_if_username_is_registered(self):
        # test method clean
        form_data = {'username': 'test-user', 'password': '12a3W@mя45'}
        form = LoginForm(data=form_data)

        self.assertTrue(User.objects.filter(username='test-user').exists())
        user = User.objects.get(username='test-user')
        self.assertTrue(check_password('12a3W@mя45', user.password))

        self.assertTrue(form.is_valid())
