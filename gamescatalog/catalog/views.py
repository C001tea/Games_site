from django.http import HttpResponse
from django.shortcuts import render
from .models import Game

def hello(request):

    games_list = Game.objects.all()[:72]

    return render(request, 'catalog/home.html', context={'games_list': games_list})