import json
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse


class HttpResponseAjax(HttpResponse):

    def __init__(self, status='ok', **kwargs):
        kwargs['status'] = status
        super(HttpResponseAjax, self).__init__(content=json.dumps(kwargs), content_type='application/json')


class HttpResponseAjaxError(HttpResponseAjax):

    def __init__(self, code, message):
        super(HttpResponseAjaxError, self).__init__(code=code, message=message)


def login_required_ajax(view):
    def new_view(request: HttpRequest, *args, **kwargs):
        if request.user.is_authenticated:
            return view(request, *args, **kwargs)
        elif request.is_ajax():
            return HttpResponseAjaxError(code='no_auth', message='This action requires authorization')
        else:
            redirect(reverse('login') + '?continue=' + request.get_full_path())
    return new_view
