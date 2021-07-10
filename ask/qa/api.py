from qa.models import Question, Answer
from django.contrib.auth.models import User
from rest_framework import serializers, viewsets, generics, routers
from rest_framework.exceptions import APIException


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']


class QuestionSerializer(serializers.ModelSerializer):
    author = serializers.DictField()

    class Meta:
        model = Question
        fields = ['title', 'text', 'added_at', 'rating', 'author']


class AnswerSerializer(serializers.ModelSerializer):
    author = serializers.DictField()
    question = serializers.CharField()

    class Meta:
        model = Answer
        fields = ['text', 'author', 'added_at', 'question']


class QuestionDoesNotExistException(APIException):
    status_code = 404
    default_detail = 'The requested question was not found.'
    default_code = 'invalid_question_id'


class UserDoesNotExistException(APIException):
    status_code = 404
    default_detail = 'The requested user was not found.'
    default_code = 'invalid_user_id'


class QuestionsListView(generics.ListAPIView):
    """
    API endpoint that allows questions to be viewed.
    """
    serializer_class = QuestionSerializer

    def get_queryset(self):
        queryset = []
        questions = Question.objects.all()
        for question in questions:
            queryset.append(
                {
                    'id': question.pk,
                    'title': question.title,
                    'text': question.text,
                    'added_at': question.added_at,
                    'rating': question.rating,
                    'author': {question.author.username: question.author.email},
                }
            )
        return queryset


class PopularQuestionsListView(generics.ListAPIView):
    """
    API endpoint that allows popular questions to be viewed.
    """
    serializer_class = QuestionSerializer

    def get_queryset(self):
        queryset = []
        questions = Question.objects.popular()
        for question in questions:
            queryset.append(
                {
                    'id': question.pk,
                    'title': question.title,
                    'text': question.text,
                    'added_at': question.added_at,
                    'rating': question.rating,
                    'author': {question.author.username: question.author.email},
                }
            )
        return queryset


class AnswersListView(generics.ListAPIView):
    """
    API endpoint that allows answers to be viewed.
    """
    serializer_class = AnswerSerializer

    def get_queryset(self):
        queryset = []
        answers = Answer.objects.all()
        for answer in answers:
            queryset.append(
                {
                    'id': answer.pk,
                    'text': answer.text,
                    'added_at': answer.added_at,
                    'author': {answer.author.username: answer.author.email},
                    'question': answer.question.title
                }
            )
        return queryset


class AnswersToQuestionListView(generics.ListAPIView):
    """
    API endpoint that allows answers to the requested question to be viewed.
    """
    serializer_class = AnswerSerializer

    def get_queryset(self):
        question_id = self.kwargs['question_id']
        try:
            question = Question.objects.get(pk=question_id)
            queryset = []
            answers = Answer.objects.filter(question=question)
            for answer in answers:
                queryset.append(
                    {
                        'id': answer.pk,
                        'text': answer.text,
                        'added_at': answer.added_at,
                        'author': {answer.author.username: answer.author.email},
                        'question': answer.question.title
                    }
                )
            return queryset
        except Question.DoesNotExist:
            raise QuestionDoesNotExistException()


class UsersQuestionsListView(generics.ListAPIView):
    """
    API endpoint that allows questions from the requested user to be viewed.
    """
    serializer_class = QuestionSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        try:
            user = User.objects.get(pk=user_id)
            queryset = []
            questions = Question.objects.filter(author=user)
            for question in questions:
                queryset.append(
                    {
                        'id': question.pk,
                        'title': question.title,
                        'text': question.text,
                        'added_at': question.added_at,
                        'rating': question.rating,
                        'author': {question.author.username: question.author.email},
                    }
                )
            return queryset
        except User.DoesNotExist:
            raise UserDoesNotExistException()


class UsersListView(generics.ListAPIView):
    """
    API endpoint that allows users to be viewed.
    """
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = User.objects.all()
        return queryset


class UsersAnswersListView(generics.ListAPIView):
    """
    API endpoint that allows answers from the requested user to be viewed.
    """
    serializer_class = AnswerSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        try:
            user = User.objects.get(pk=user_id)
            queryset = []
            answers = Answer.objects.filter(author=user)
            for answer in answers:
                queryset.append(
                    {
                        'id': answer.pk,
                        'text': answer.text,
                        'added_at': answer.added_at,
                        'author': {answer.author.username: answer.author.email},
                        'question': answer.question.title
                    }
                )
            return queryset
        except User.DoesNotExist:
            raise UserDoesNotExistException()


class LikesToQuestionListView(generics.ListAPIView):
    """
    API endpoint that allows users who rated the requested question to be viewed.
    """
    serializer_class = UserSerializer

    def get_queryset(self):
        question_id = self.kwargs['question_id']
        try:
            question = Question.objects.get(pk=question_id)
            queryset = User.objects.filter(questions=question)
            return queryset
        except Question.DoesNotExist:
            raise QuestionDoesNotExistException()

