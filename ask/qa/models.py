from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class QuestionManager(models.Manager):

    def new(self):
        return self.order_by('-added_at')

    def popular(self):
        return self.order_by('-rating')


class Question(models.Model):
    title = models.CharField(default="", max_length=1024)
    text = models.TextField(default="")
    added_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    likes = models.ManyToManyField(User, related_name='questions',
                                   through='QuestionLikes', through_fields=('question', 'user'))
    objects = QuestionManager()

    def get_absolute_url(self):
        return reverse('question', kwargs={'id': str(self.id)})


class Answer(models.Model):
    text = models.TextField(default="")
    added_at = models.DateTimeField(auto_now_add=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)


class QuestionLikes(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='question_likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='question_likes')
    is_liked = models.BooleanField()
