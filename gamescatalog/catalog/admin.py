from django.contrib import admin
from .models import Game, Store, Rating, Requirement, Screenshot, GamePrice, Platform


@admin.register(Game)
class AdminGame(admin.ModelAdmin):
    list_display = ['name', 'released', 'rating', 'steam_id']
    list_filter = ('stores', 'genres')
    search_fields = ['name']

@admin.register(Store)
class AdminStore(admin.ModelAdmin):
    list_display = ['id', 'name']

@admin.register(GamePrice)
class AdminGamePrice(admin.ModelAdmin):
    list_display = ['game', 'store', 'price', 'retail_price', 'savings', 'url']
    search_fields = ['game__name']

@admin.register(Screenshot)
class AdminScreenshot(admin.ModelAdmin):
    list_display = ['game__name', 'image']
    search_fields = ['game__name']

@admin.register(Platform)
class AdminPlatform(admin.ModelAdmin):
    list_display = ['name', 'slug']