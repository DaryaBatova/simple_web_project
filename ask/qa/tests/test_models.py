from django.test import TestCase
from django.urls import resolve
from django.http import HttpRequest

from qa.views import *

from qa.models import Question, Answer, QuestionLikes
from django.contrib.auth.models import User


class QuestionModelTest(TestCase):

    def test_get_absolute_url(self):
        q = Question.objects.create()
        self.assertEqual(q.get_absolute_url(), f'/question/{q.id}/')

    def test_default_title_label(self):
        q = Question()
        self.assertEqual(q.title, "")

    def test_default_text_label(self):
        q = Question()
        self.assertEqual(q.text, "")

    def test_default_added_at_label(self):
        q = Question()
        self.assertEqual(q.added_at, None)

    def test_default_rating_label(self):
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
        # q.likes.add(user)
        QuestionLikes.objects.create(question=q, user=user, is_liked=True)
        q_in_db = Question.objects.get(id=q.id)
        self.assertIn(user, q_in_db.likes.all())

    def test_on_delete(self):
        user = User.objects.create(email='a@b.com')
        q = Question.objects.create(author=user)
        q_in_db = Question.objects.get(id=q.id)
        self.assertEqual(q_in_db.author, user)
        # User.objects.get(id=user.id).delete()
        # self.assertEqual(q_in_db.author, None)

    def test_question_manager_method_new(self):
        q1 = Question.objects.create()
        q2 = Question.objects.create()
        q3 = Question.objects.create()
        self.assertEqual(
            list(Question.objects.new().all()),
            [q3, q2, q1]
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

    def test_default_text_label(self):
        a = Answer()
        self.assertEqual(a.text, "")

    def test_default_added_at_label(self):
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


class M2MThroughTest(TestCase):

    def setUp(self):
        # Create three questions:
        self.q1 = Question.objects.create(title='Question 1')
        self.q2 = Question.objects.create(title='Question 2')
        self.q3 = Question.objects.create(title='Question 3')

        # And three users:
        self.joe = User.objects.create(username='Joe')
        self.jim = User.objects.create(username='Jim')
        self.bob = User.objects.create(username='Bob')

        # Every user rated every question
        QuestionLikes.objects.create(user=self.joe, question=self.q1, is_liked=True)
        QuestionLikes.objects.create(user=self.jim, question=self.q1, is_liked=False)
        QuestionLikes.objects.create(user=self.bob, question=self.q1, is_liked=False)

        QuestionLikes.objects.create(user=self.joe, question=self.q2, is_liked=False)
        QuestionLikes.objects.create(user=self.jim, question=self.q2, is_liked=True)
        QuestionLikes.objects.create(user=self.bob, question=self.q2, is_liked=False)

        QuestionLikes.objects.create(user=self.joe, question=self.q3, is_liked=False)
        QuestionLikes.objects.create(user=self.jim, question=self.q3, is_liked=False)
        QuestionLikes.objects.create(user=self.bob, question=self.q3, is_liked=True)

    def test_questions_that_the_user_JIM_has_rated(self):
        # What questions did Jim rate?
        jims_questions = Question.objects.filter(likes=self.jim)
        self.assertEqual(list(jims_questions), [self.q1, self.q2, self.q3])

    def test_questions_that_the_user_JIM_has_liked(self):
        jims_liked_questions = Question.objects.filter(likes=self.jim, question_likes__is_liked=True)
        self.assertEqual(list(jims_liked_questions), [self.q2])

    def test_questions_that_the_user_JIM_has_disliked(self):
        jims_liked_questions = Question.objects.filter(likes=self.jim, question_likes__is_liked=False)
        self.assertEqual(list(jims_liked_questions), [self.q1, self.q3])

    def test_users_who_rated_the_FIRST_question(self):
        users_rating_q1 = User.objects.filter(questions=self.q1)
        self.assertEqual(list(users_rating_q1), [self.joe, self.jim, self.bob])

    def test_users_who_liked_the_FIRST_question(self):
        users_liked_q1 = User.objects.filter(questions=self.q1, question_likes__is_liked=True)
        self.assertEqual(list(users_liked_q1), [self.joe])

    def test_users_who_disliked_the_FIRST_question(self):
        users_disliked_q1 = User.objects.filter(questions=self.q1, question_likes__is_liked=False)
        self.assertEqual(list(users_disliked_q1), [self.jim, self.bob])

    def test_this_user_has_rated_this_question(self):
        # user Bob has rated the first question
        self.assertTrue(self.q1 in Question.objects.filter(likes=self.bob))

        # and Bob has disliked the first question
        row = QuestionLikes.objects.get(question=self.q1, user=self.bob)
        self.assertFalse(row.is_liked)

        new_user = User.objects.create(username='new_user')
        # new_user hasn't rated the first question
        self.assertFalse(self.q1 in Question.objects.filter(likes=new_user))
