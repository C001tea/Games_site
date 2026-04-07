from django.shortcuts import render
from .models import Game, Store, Platform
import meilisearch
from django.db.models import Case, When

client = meilisearch.Client('http://127.0.0.1:7700', 'artem')

def home(request):

    sort = (request.GET.get("sort", "") or "rating")

    sort_map = {
        "rating": "-rating"

    }

    games_list = Game.objects.all().order_by(sort_map.get(sort, "rating"))[:72]

    return render(request, 'catalog/home.html', context={'games_list': games_list})


def search(request):
    searched = request.GET.get('q')

    games = []

    if searched:
        search_result = client.index('games').search(searched, {
            'limit': 20,
            'sort': ['rating:desc']
        })
        found_ids = [hit['id'] for hit in search_result['hits']]
        if found_ids:
            preserved_orders = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(found_ids)])
            games = Game.objects.filter(id__in=found_ids).order_by(preserved_orders)
    context = {'games_list': games, 'searched': searched}
    return render(request, 'catalog/search.html', context=context)


def game_detail(request, slug):
    game = Game.objects.get(slug=slug)
    prices = game.prices.all()
    return render(request, 'catalog/detail_games.html', context={'game': game, 'prices': prices})


def platforms(request):
    platform_list = Platform.objects.all()
    return render(request, 'catalog/platforms.html', {"platform_list": platform_list})