from django.http import HttpResponse
from django.shortcuts import render
from .models import Games

def hello(request):

    games_list = Games.objects.all()[:10]

    return render(request, 'catalog/home.html', context={'games_list': games_list})