from django.http import HttpResponse
from django.shortcuts import render


def start_page(request):
    tmp_dict = dict()
    return render(request, 'index.html', tmp_dict)
