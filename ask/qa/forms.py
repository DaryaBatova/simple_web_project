from django import forms
from django.contrib.auth.models import User

from qa.models import Question

EMPTY_TITLE_ERROR = "You can't have an empty question title"
EMPTY_TEXT_ERROR = "You can't have an empty question text"


class AskForm(forms.Form):
    title = forms.CharField(max_length=1024, label="Question title",
                            error_messages={'required': EMPTY_TITLE_ERROR})
    text = forms.CharField(widget=forms.Textarea, label="Question text",
                            error_messages={'required': EMPTY_TEXT_ERROR})

    def clean(self):
        pass

    def save(self):
        question = Question(**self.cleaned_data)
        question.save()
        return question
