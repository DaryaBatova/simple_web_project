import re
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password

from qa.models import Question, Answer

EMPTY_TITLE_ERROR = "You can't have an empty question title"
EMPTY_TEXT_ERROR = "You can't have an empty text"

EMPTY_USERNAME_ERROR = "You can't have an empty username"
EMPTY_EMAIL_ERROR = "You can't have an empty email"
EMPTY_PASSWORD_ERROR = "You can't have an empty password"


class AskForm(forms.Form):
    title = forms.CharField(max_length=1024, label="Question title", error_messages={'required': EMPTY_TITLE_ERROR})
    text = forms.CharField(widget=forms.Textarea, label="Question text", error_messages={'required': EMPTY_TEXT_ERROR})

    def clean(self):
        pass

    def save(self):
        question = Question(**self.cleaned_data)
        question.save()
        return question


class AnswerForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea, label="Answer text", error_messages={'required': EMPTY_TEXT_ERROR})
    question = forms.IntegerField(widget=forms.HiddenInput)

    def clean_question(self):
        question_id = self.cleaned_data['question']
        try:
            question = Question.objects.get(pk=question_id)
        except Question.DoesNotExist:
            raise forms.ValidationError("This question doesn't exist")
        return question

    def clean(self):
        pass

    def save(self):
        answer = Answer(**self.cleaned_data)
        answer.save()
        return answer


class SignupForm(forms.Form):
    username = forms.CharField(max_length=100, error_messages={'required': EMPTY_USERNAME_ERROR})
    email = forms.EmailField(error_messages={'required': EMPTY_EMAIL_ERROR})
    password = forms.CharField(widget=forms.PasswordInput, max_length=256,
                               error_messages={'required': EMPTY_PASSWORD_ERROR})

    @staticmethod
    def password_check(a):
        res = [re.search(r"[a-z]", a), re.search(r"[A-Z]", a), re.search(r"[0-9]", a), re.search(r"\W", a)]
        if all(res):
            return "Password is okay"
        return ("Password is weak. Add "+
                "lowercase letters, "*(res[0] is None) +
                "uppercase letters, "*(res[1] is None) +
                "digits, "*(res[2] is None) +
                "special symbols, "*(res[3] is None) +
                "then try again")

    def clean_username(self):
        username = self.cleaned_data['username']
        if username in User.objects.values_list('username', flat=True):
            raise forms.ValidationError("A user with the same name already exists")
        return username

    def clean_password(self):
        password = self.cleaned_data['password']
        # included Django validators
        validate_password(password)
        # own validator
        pass_check = self.password_check(password)
        if pass_check != "Password is okay":
            raise forms.ValidationError(pass_check)
        return make_password(password)

    def save(self):
        user = User(**self.cleaned_data)
        user.save()
        return user
