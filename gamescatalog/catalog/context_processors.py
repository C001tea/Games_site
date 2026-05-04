from .models import Store, Game, GamePrice, Genre, Platform, Tag, Screenshot
from django.core.cache import cache


def global_var(request):
    stores = cache.get("all_stores")

    if not stores:
        stores = Store.objects.all()
        cache.set("all_games", stores, 3600)
    return {
        "all_stores": stores,
        "all_games": Game.objects.all(),
        "all_genres": Genre.objects.all(),
        "all_platforms": Platform.objects.all(),
    }