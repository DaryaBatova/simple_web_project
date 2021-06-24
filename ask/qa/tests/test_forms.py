from django.test import TestCase

from qa.forms import (
    EMPTY_TITLE_ERROR, EMPTY_TEXT_ERROR, AskForm, AnswerForm
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
        form = AskForm(data={'title':'', 'text': ''})
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
        # post request to non-existen question
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
