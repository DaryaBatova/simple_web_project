from django.urls import path
from .views import *


urlpatterns = [
    path('', question_list_new, name='new_questions'),
    path('login/', test, name='login'),
    path('signup/', test, name='signup'),
    path('question/<int:id>/', question_view, name='question'),
    path('ask/', test, name='ask'),
    path('popular/', question_list_popular, name='popular'),
    path('new/', test, name='new'),
]
