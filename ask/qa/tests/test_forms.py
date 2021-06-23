from django.test import TestCase

from qa.forms import (
    EMPTY_TITLE_ERROR, EMPTY_TEXT_ERROR, AskForm
)

from qa.models import Question

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

