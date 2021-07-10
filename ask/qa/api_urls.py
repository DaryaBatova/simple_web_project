from django.urls import path
from .api import *


urlpatterns = [
    path('questions/', QuestionsListView.as_view(), name='api_questions'),
    path('questions/popular/', PopularQuestionsListView.as_view(), name='api_popular_questions'),
    path('answers/', AnswersListView.as_view(), name='api_answers'),
    path('question/<int:question_id>/answers/', AnswersToQuestionListView.as_view(), name='api_answers_to_question'),
    path('user/<int:user_id>/questions/', UsersQuestionsListView.as_view(), name='api_users_questions'),
    path('users/', UsersListView.as_view(), name='api_users'),
    path('user/<int:user_id>/answers/', UsersAnswersListView.as_view(), name='api_users_answers'),
    path('question/<int:question_id>/likes/', LikesToQuestionListView.as_view(), name='api_question_likes'),
]