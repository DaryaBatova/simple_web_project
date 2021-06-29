from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.http import Http404
from django.core.paginator import Paginator
from django.urls import reverse
from qa.models import Question
from qa.forms import AskForm, AnswerForm, SignupForm


def test(request, *args, **kwargs):
    return HttpResponse('OK')


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


def question_view(request, id):
    question = get_object_or_404(Question, pk=id)
    if request.method == 'POST':
        request.POST = request.POST.copy()
        request.POST['question'] = question.id
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save()
            question = answer.question
            return HttpResponseRedirect(question.get_absolute_url())
    else:
        form = AnswerForm()
    content = {
        'question': question,
        'answers': question.answer_set.all(),
        'form': form
    }
    return render(request, 'question.html', content)


def ask_add(request):
    if request.method == 'POST':
        form = AskForm(request.POST)
        if form.is_valid():
            question = form.save()
            return HttpResponseRedirect(question.get_absolute_url())
    else:
        form = AskForm()
    return render(request, 'ask_form.html', {'form': form})


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            # TODO вход на сайт
            return HttpResponseRedirect(reverse('new_questions'))
    else:
        form = SignupForm()
    return render(request, 'signup_form.html', {'form': form})
