from django.contrib import admin
from . import models

@admin.register(models.Game)
class AdminGame(admin.ModelAdmin):
    list_display = ['name', 'released', 'rating', 'steam_id', 'alternative_names', 'developers', 'added', 'parent_platforms']
    list_filter = ('stores', 'genres', 'released', 'tags')
    search_fields = ['name', 'alternative_names']

@admin.register(models.Store)
class AdminStore(admin.ModelAdmin):
    list_display = ['id', 'name', 'domain']

@admin.register(models.GamePrice)
class AdminGamePrice(admin.ModelAdmin):
    list_display = ['game', 'store', 'price', 'retail_price', 'savings', 'url']
    search_fields = ['game__name']

@admin.register(models.Screenshot)
class AdminScreenshot(admin.ModelAdmin):
    list_display = ['game__name', 'image']
    search_fields = ['game__name']

@admin.register(models.Platform)
class AdminPlatform(admin.ModelAdmin):
    list_display = ['name', 'slug']

@admin.register(models.Requirement)
class AdminRequirement(admin.ModelAdmin):
    search_fields = ["game__name"]
    list_display = ["game", "platform_name", ]

@admin.register(models.Tag)
class AdminTag(admin.ModelAdmin):
    list_display = ["id", "name", "slug"]
    search_fields = ["name"]


@admin.register(models.PriceHistory)
class AdminPriceHistory(admin.ModelAdmin):
    list_display = ["id", "game", "store", "date", "price"]

@admin.register(models.WishList)
class AdminWishlist(admin.ModelAdmin):
    list_display = ["id", "user", "game", "is_active", "send_notification"]

@admin.register(models.Article)
class AdminArticle(admin.ModelAdmin):
    list_display = ["title", "related_game", "is_published", "published_at"]
    list_filter = ('is_published',)
    search_fields = ('title', 'content', 'related_game', )
    prepopulated_fields = {'slug': ('title', )}
    autocomplete_fields = ('related_game', )