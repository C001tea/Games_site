from django.contrib import admin
from .models import Game, Store, Rating, Requirement, Screenshot, GamePrice


@admin.register(Game)
class AdminGame(admin.ModelAdmin):
    list_display = ['name', 'released', 'rating', 'steam_id']
    list_filter = ('stores', 'genres')

@admin.register(Store)
class AdminStore(admin.ModelAdmin):
    list_display = ['id', 'name']

@admin.register(GamePrice)
class AdminGamePrice(admin.ModelAdmin):
    list_display = ['game', 'store', 'price', 'retail_price', 'savings', 'url']