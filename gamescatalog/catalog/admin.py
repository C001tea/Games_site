from django.contrib import admin
from .models import Game, Store, Rating, Requirement, Screenshot, GamePrice, Platform, Tag


@admin.register(Game)
class AdminGame(admin.ModelAdmin):
    list_display = ['name', 'released', 'rating', 'steam_id', 'alternative_names', 'developers', 'added', 'parent_platforms']
    list_filter = ('stores', 'genres', 'released', 'tags')
    search_fields = ['name', 'alternative_names']

@admin.register(Store)
class AdminStore(admin.ModelAdmin):
    list_display = ['id', 'name', 'domain']

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

@admin.register(Requirement)
class AdminRequirement(admin.ModelAdmin):
    search_fields = ["game__name"]
    list_display = ["game", "platform_name", ]

@admin.register(Tag)
class AdminTag(admin.ModelAdmin):
    list_display = ["id", "name", "slug"]
    search_fields = ["name"]