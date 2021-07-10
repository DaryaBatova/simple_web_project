from django.urls import path
from .views import *


urlpatterns = [
    path('', question_list_new, name='new_questions'),
    path('login/', login_view, name='login'),
    path('signup/', signup, name='signup'),
    path('question/<int:id>/', question_view, name='question'),
    path('ask/', ask_add, name='ask'),
    path('popular/', question_list_popular, name='popular'),
    path('like/', add_like_to_the_question, name='like'),
    path('logout/', logout_view, name='logout'),
    path('answers/delete/', delete_answer, name='delete_answer'),
    path('my-questions/', users_question_list, name='my_questions'),
    path('question/<int:question_id>/delete/', delete_question, name='delete_question'),
]
