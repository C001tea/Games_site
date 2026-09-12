from django.db.models.functions import TruncDate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import Game, Store, Platform, GamePrice, Genre, WishList, Article
import meilisearch
from django.db.models import Case, When, Count
from django.core.paginator import Paginator
from django.db.models import F, Min, Max
import random, os

client = meilisearch.Client("http://20.91.196.239:7700", os.getenv('MEILI_MASTER_KEY'))

def home(request):
    games_list = Game.objects.all()


    games_discount = list(games_list.annotate(discount=Max('prices__savings')).order_by(F('discount').desc(nulls_last=True))[:60])
    games_released = list(games_list.order_by(F("released").desc(nulls_last=True))[:60])
    games_popular = list(games_list.order_by(F("added").desc(nulls_last=True))[:60])
    games_cheap = list(Game.objects.annotate(min_price=Min('prices__price')).order_by(F('min_price').asc(nulls_last=True))[:60])

    most_discount = random.sample(games_discount, min(10, len(games_discount)))
    new_releases = random.sample(games_released, min(10, len(games_released)))
    popular = random.sample(games_popular, min(10, len(games_popular)))
    cheap_offers = random.sample(games_cheap, min(10, len(games_cheap)))

    offers_list = {"discount": {"Biggest Discount Today": most_discount},
                   "newest": {"New Releases": new_releases},
                   "popular": {"Popular": popular},
                   "price-low-to-high": {"Cheapest Offers": cheap_offers},
                   }

    return render(request, 'catalog/home.html', context={'games_list': games_list, "offers_list": offers_list})


def search(request):
    searched = request.GET.get('q')

    games = []

    if searched:
        search_result = client.index('games').search(searched, {
            'limit': 21,
            'sort': ['added:desc']
        })
        found_ids = [hit['id'] for hit in search_result['hits']]
        if found_ids:
            preserved_orders = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(found_ids)])
            games = Game.objects.filter(id__in=found_ids).order_by(preserved_orders)
    context = {'games_list': games, 'searched': searched}
    return render(request, 'catalog/search.html', context=context)


def game_detail(request, slug):
    game = Game.objects.get(slug=slug)
    in_wishlist = request.user.is_authenticated and WishList.objects.filter(user=request.user, game=game).exists()
    current_tags = game.tags.all()

    similar_games_pool = list(Game.objects.filter(
        tags__in=current_tags
    ).exclude(
        id=game.id).annotate(
        matching_tags=Count('tags')
    ).order_by('-matching_tags')[:30])

    if len(similar_games_pool) >= 5:
        similar_games = random.sample(similar_games_pool, min(len(similar_games_pool), 10))
    else:
        similar_games = similar_games_pool
    game_prices = game.prices.all().order_by('price')

    price_history_qs = game.price_history.annotate(day=TruncDate('date')).values('day').annotate(min_price=Min('price')).order_by('date')[:60]

    price_history_data = []
    for entry in price_history_qs:
        record = (
            game.price_history
            .filter(
                date=entry['day'],
                price=entry['min_price']
            )
            .select_related('store')
            .first()
        )

        if record:
            price_history_data.append({
                'date': entry['day'].strftime('%Y-%m-%d'),
                'price': round(float(entry['min_price']), 2),
                'store': record.store.name,
            })


    ratings = { rating.title: rating.count for rating in game.detail_ratings.all()}
    user_ratings = game.ratings.values('score').annotate(count=Count('score'))

    for rating in user_ratings:
        ratings[rating['score']] = ratings.get(rating['score'], 0) + rating['count']

    total = sum(ratings.values())
    percents = {k: round(v*100/total, 1) for k, v in ratings.items()}

    return render(request, 'catalog/detail_games.html', context={
        'game': game,
        'game_prices': game_prices,
        'similar_games': similar_games,
        'tags_list': current_tags,
        'in_wishlist': in_wishlist,
        'price_history_json': price_history_data,
        'price_history': price_history_qs,
        'percents': percents,
        'total_rating': total,
        })


def platforms(request):
    platform_list = Platform.objects.annotate(games_count=Count('games')).order_by('-games_count')
    return render(request, 'catalog/platforms.html', {"platform_list": platform_list})


def all_games(request):
    sort = request.GET.get("sort", "rating")
    platform_slug = request.GET.get("platform")
    genre_name = request.GET.get("genre")
    store_name = request.GET.get("store")

    platform_list = Platform.objects.all().order_by("name")
    genres_list = Genre.objects.all().order_by("name")
    stores_list = Store.objects.all().order_by("name")

    sorting_map = {
        "oldest": F("released").asc(nulls_last=True),
        "newest": F("released").desc(nulls_last=True),
        "rating": F("rating").desc(nulls_last=True),
        "popular": F("added").desc(nulls_last=True),
        "price-low-to-high": F("min_price").asc(nulls_last=True),
        "price-high-to-low": F("min_price").desc(nulls_last=True)
    }
    games_list = Game.objects.all()

    if sort in ("price-low-to-high", "price-high-to-low"):
        games_list = games_list.annotate(min_price=Min("prices__price"))

    if platform_slug:
        games_list = games_list.filter(platforms__slug=platform_slug)

    if genre_name:
        games_list = games_list.filter(genres__name=genre_name)

    if store_name:
        games_list = games_list.filter(stores__name=store_name)

    games_list = games_list.order_by(sorting_map.get(sort, F("rating").desc(nulls_last=True)))

    paginator = Paginator(games_list, 24)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    page_range = get_page_range(page_obj.number, page_obj.paginator.num_pages)

    return render(request, 'catalog/all_games.html', {'games_list': page_obj,
                                                      'platform_list': platform_list,
                                                      'genres_list': genres_list,
                                                      'page_range': page_range,
                                                      'stores_list': stores_list})


def genres(request):
    genres_list = Genre.objects.all().order_by("name")

    return render(request, 'catalog/genres.html', context={"genres_list": genres_list})

def stores(request):
    stores_list = Store.objects.all().order_by("name")
    return render(request, 'catalog/stores.html', context={"stores_list": stores_list})


def get_page_range(current_page, num_pages):
    delta = 2
    pages = list()

    pages.append(1)

    left = current_page - delta
    right = current_page + delta

    if left > 2:
        pages.append('...')
    for num in range(left, right + 1):
        if 1 < num < num_pages:
            pages.append(num)

    if right < num_pages - 1:
        pages.append('...')

    if num_pages > 1:
        pages.append(num_pages)

    return pages



@login_required
def wishlist_page(request):

    items = WishList.objects.filter(
        user=request.user,
        is_active=True
    ).select_related('game').prefetch_related('game__prices__store')

    for item in items:
        item.min_price = item.game.prices.filter(
            price__isnull = False
        ).order_by('price').first()

    return render(request, 'catalog/wishlist.html', {'items': items})


def remove_from_wishlist(request, game_id):
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'auth_required',
            'message': 'You must be logged in to add games to your wishlist.'
        }, status=401)

    if request.method == 'POST':
        WishList.objects.filter(user=request.user, game_id=game_id).delete()

    return redirect('wishlist')

def add_to_wishlist(request, game_id):

    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'auth_required',
            'message': 'You must be logged in to add games to your wishlist.'
        }, status=401)

    if request.method == 'POST':

        game = get_object_or_404(Game, id=game_id)
        obj, created = WishList.objects.get_or_create(user=request.user, game=game)
        return JsonResponse({'created': created})

    return JsonResponse({'error': 'Method is not allowed'}, status=405)

@login_required
def game_rate(request, game_id):
    if request.status == "POST":
        score = request.POST.get('score')

        if score not in ['exceptional', 'recommended', 'meh', 'skip']:
            return JsonResponse({'error': 'Invalid score'}, status=400)



    return JsonResponse({'error': 'Method is not allowed'}, status=405)

@login_required
def set_notification(request, game_id):
    if request.method == 'POST':
        value = request.POST.get('value') == 'true'
        item = WishList.objects.get(user=request.user, game_id=game_id)
        item.send_notification = value
        item.save()
        return JsonResponse({"send_notification": item.send_notification})
    return JsonResponse({'error': 'Method not allowed'}, status=405)


def articles_list(request):
    articles = Article.objects.filter(is_published=True)
    return render(request, 'catalog/articles_list.html', context={'articles': articles})

def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug, is_published=True)
    return render(request, 'catalog/article_detail.html', {'article': article})