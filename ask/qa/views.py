from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.http import Http404
from django.core.paginator import Paginator
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from qa.models import Question, Answer, QuestionLikes
from qa.forms import AskForm, AnswerForm, SignupForm, LoginForm
from .ajax import HttpResponseAjax, HttpResponseAjaxError, login_required_ajax


def paginate(request, qs, base_url):
    limit = 10
    page = request.GET.get('page', 1)
    try:
        page = int(page)
    except ValueError:
        raise Http404
    paginator = Paginator(qs, limit)
    paginator.baseurl = base_url
    try:
        page = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages
        page = paginator.page(page)
    content = {
        'questions': page.object_list,
        'paginator': paginator,
        'page': page
    }
    return render(request, 'questions_new.html', content)


def question_list_new(request):
    qs = Question.objects.new()
    return paginate(request, qs, base_url='/?page=')


def question_list_popular(request):
    qs = Question.objects.popular()
    return paginate(request, qs, base_url=reverse('popular') + '?page=')


@login_required(login_url='/login/')
def users_question_list(request):
    qs = Question.objects.filter(author=request.user).order_by('-added_at')
    return paginate(request, qs, base_url=reverse('my_questions') + '?page=') 


def question_view(request, id):
    question = get_object_or_404(Question, pk=id)
    if request.method == 'POST':
        request.POST = request.POST.copy()
        request.POST['question'] = question.id
        form = AnswerForm(request.POST)
        if form.is_valid():
            if not request.user.is_authenticated:
                return HttpResponseRedirect(reverse('login'))
            answer = form.save()
            answer.author = request.user
            answer.save()
            question = answer.question
            return HttpResponseRedirect(question.get_absolute_url())
    else:
        form = AnswerForm()

    content = {
        'question': question,
        'answers': question.answer_set.all(),
        'form': form,
        'session': request.session,
        'user': request.user
    }

    if request.user.is_authenticated:
        if question in Question.objects.filter(likes=request.user):
            button_like = QuestionLikes.objects.get(question=question, user=request.user).is_liked
            content['button_like'] = button_like
    return render(request, 'question.html', content)


def ask_add(request):
    if request.method == 'POST':
        form = AskForm(request.POST)
        if form.is_valid():
            if not request.user.is_authenticated:
                return HttpResponseRedirect(reverse('login'))
            question = form.save()
            question.author = request.user
            question.save()
            return HttpResponseRedirect(question.get_absolute_url())
    else:
        form = AskForm()
    return render(request, 'ask_form.html', {'form': form, 'session': request.session, 'user': request.user})


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return HttpResponseRedirect(reverse('new_questions'))
    else:
        form = SignupForm()
    return render(request, 'signup_form.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse('new_questions'))
    else:
        form = LoginForm()
    return render(request, 'login_form.html', {'form': form, 'session': request.session, 'user': request.user})


def logout_view(request):
    if request.user is not None:
        logout(request)
        return HttpResponseRedirect(reverse('new_questions'))


@login_required_ajax
def add_like_to_the_question(request):
    user = request.user
    question = get_object_or_404(Question, pk=request.POST.get('question_id'))
    operation = request.POST.get('operation')
    # if user is authenticated
    if question in Question.objects.filter(likes=user):
        # request user has rated this question
        row = QuestionLikes.objects.get(question=question, user=user)
        if row.is_liked and operation == 'Dislike':
            question.rating -= 2
            row.is_liked = False
            row.save()
        elif row.is_liked and operation == 'Like':
            question.rating -= 1
            row.delete()
        elif not row.is_liked and operation == 'Like':
            question.rating += 2
            row.is_liked = True
            row.save()
        elif not row.is_liked and operation == 'Dislike':
            question.rating += 1
            row.delete()
    else:
        # request user hasn't rated this question
        QuestionLikes.objects.create(question=question, user=user, is_liked=(operation == 'Like'))
        if operation == 'Like':
            question.rating += 1
        elif operation == 'Dislike':
            question.rating -= 1
    question.save()

    if question:
        return HttpResponseAjax(message='Your rating is accepted')

    return HttpResponseAjaxError(code='bad_params', message='Question does not exist')


def delete_answer(request):
    # id in request.POST
    answer = get_object_or_404(Answer, pk=request.POST.get('answer_id')) 
    if request.user == answer.author:
        answer.delete()
    # return HttpResponseRedirect(answer.question.get_absolute_url())
    return HttpResponseAjax(message='Your answer has been successfully deleted!')

def delete_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.user == question.author:
        question.delete()
    return HttpResponseRedirect(reverse('my_questions'))
