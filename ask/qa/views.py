from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.http import Http404
from django.core.paginator import Paginator
from qa.models import Question

def test(request, *args, **kwargs):
    return HttpResponse('OK')

def paginate(request, qs, base_url):
    # qs = Question.objects.popular()
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
    return paginate(request, qs, base_url='/popular/?page=')

def question_view(request, id):
    question = get_object_or_404(Question, pk=id)
    content = {
        'question': question,
        'answers': question.answer_set.all()
    }
    return render(request, 'question.html', content)
