from django.shortcuts import render
from .models import Game, Store, Platform, GamePrice, Genre
import meilisearch
from django.db.models import Case, When, Count
from django.core.paginator import Paginator
from django.db.models import F, Min

client = meilisearch.Client('http://127.0.0.1:7700', 'artem')

def home(request):
    games_list = Game.objects.all()

    new_releases = games_list.order_by(F("released").desc(nulls_last=True))[:10]
    popular = games_list.order_by(F("added").desc(nulls_last=True))[:10]
    cheap_offers = Game.objects.annotate(min_price=Min('prices__price')).order_by(F('min_price').asc(nulls_last=True))

    offers_list = {"New Releases": new_releases, "Popular": popular, "Cheapest Offers": cheap_offers}

    return render(request, 'catalog/home.html', context={'games_list': games_list, "offers_list": offers_list})


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
    game_prices = game.prices.all().order_by('price')
    return render(request, 'catalog/detail_games.html', context={'game': game, 'game_prices': game_prices})


def platforms(request):
    platform_list = Platform.objects.annotate(games_count=Count('games')).order_by('-games_count')
    return render(request, 'catalog/platforms.html', {"platform_list": platform_list})


def all_games(request):
    sort = request.GET.get("sort", "rating")
    platform_slug = request.GET.get("platform")
    genre_name = request.GET.get("genre")

    platform_list = Platform.objects.all().order_by("name")
    genres_list = Genre.objects.all().order_by("name")

    sorting_map = {
        "oldest": F("released").asc(nulls_last=True),
        "newest": F("released").desc(nulls_last=True),
        "rating": F("rating").desc(nulls_last=True)
    }
    games_list = Game.objects.all()

    if platform_slug:
        games_list = games_list.filter(platforms__slug=platform_slug)

    if genre_name:
        games_list = games_list.filter(genres__name=genre_name)

    games_list = games_list.order_by(sorting_map.get(sort, F("rating").desc(nulls_last=True)))

    paginator = Paginator(games_list, 21)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'catalog/all_games.html', {'games_list': page_obj, 'platform_list': platform_list, "genres_list": genres_list})


def genres(request):

    genres_list = Genre.objects.all().order_by("name")

    return render(request, 'catalog/genres.html', context={"genres_list": genres_list})