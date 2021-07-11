from qa.models import Question, Answer, QuestionLikes
from django.contrib.auth.models import User
from rest_framework import serializers, viewsets, generics, routers
from rest_framework.exceptions import APIException


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']


class UserLikeSerializer(serializers.ModelSerializer):
    rate = serializers.CharField()

    class Meta:
        model = User
        fields = ['username', 'email', 'rate']


class QuestionSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['title', 'text', 'added_at', 'rating', 'author']

    def get_author(self, obj):
        return {obj.author.username: obj.author.email}


class QuestionLikeSerializer(serializers.ModelSerializer):
    rate = serializers.CharField()

    class Meta:
        model = Question
        fields = ['title', 'text', 'added_at', 'rating', 'rate']


class AnswerSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    question = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = ['text', 'author', 'added_at', 'question']

    def get_author(self, obj):
        return {obj.author.username: obj.author.email}

    def get_question(self, obj):
        return obj.question.title


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
    queryset = Question.objects.all()


class PopularQuestionsListView(generics.ListAPIView):
    """
    API endpoint that allows popular questions to be viewed.
    """
    serializer_class = QuestionSerializer
    queryset = Question.objects.popular()


class AnswersListView(generics.ListAPIView):
    """
    API endpoint that allows answers to be viewed.
    """
    serializer_class = AnswerSerializer
    queryset = Answer.objects.all()


class AnswersToQuestionListView(generics.ListAPIView):
    """
    API endpoint that allows answers to the requested question to be viewed.
    """
    serializer_class = AnswerSerializer

    def get_queryset(self):
        question_id = self.kwargs['question_id']
        try:
            question = Question.objects.get(pk=question_id)
            queryset = Answer.objects.filter(question=question)
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
            queryset = Question.objects.filter(author=user)
            return queryset
        except User.DoesNotExist:
            raise UserDoesNotExistException()


class UsersListView(generics.ListAPIView):
    """
    API endpoint that allows users to be viewed.
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()


class UsersAnswersListView(generics.ListAPIView):
    """
    API endpoint that allows answers from the requested user to be viewed.
    """
    serializer_class = AnswerSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        try:
            user = User.objects.get(pk=user_id)
            queryset = Answer.objects.filter(author=user)
            return queryset
        except User.DoesNotExist:
            raise UserDoesNotExistException()


class LikesToQuestionListView(generics.ListAPIView):
    """
    API endpoint that allows users who rated the requested question to be viewed.
    """
    serializer_class = UserLikeSerializer

    def get_queryset(self):
        question_id = self.kwargs['question_id']
        try:
            question = Question.objects.get(pk=question_id)
            queryset = []
            users = User.objects.filter(questions=question, question_likes__is_liked=True)
            for user in users:
                rate = 'Like' if QuestionLikes.objects.get(user=user, question=question).is_liked else 'Dislike'
                queryset.append(
                    {
                        'username': user.username,
                        'email': user.email,
                        'rate': rate,
                    }
                )
            return queryset
        except Question.DoesNotExist:
            raise QuestionDoesNotExistException()


class QuestionsLikesByUserListView(generics.ListAPIView):
    """
    API endpoint that allows questions rated by the requested user to be viewed.
    """
    serializer_class = QuestionLikeSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        try:
            user = User.objects.get(pk=user_id)
            queryset = []
            questions = Question.objects.filter(likes=user)
            for question in questions:
                rate = 'Like' if QuestionLikes.objects.get(user=user, question=question).is_liked else 'Dislike'
                queryset.append(
                    {
                        'id': question.pk,
                        'title': question.title,
                        'text': question.text,
                        'added_at': question.added_at,
                        'rating': question.rating,
                        'rate': rate
                    }
                )
            return queryset
        except User.DoesNotExist:
            raise UserDoesNotExistException()

