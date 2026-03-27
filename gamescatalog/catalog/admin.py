from django.contrib import admin
from .models import Games, Store, Ratings, Requirements, Screenshots, GamePrice


@admin.register(Games)
class AdminGame(admin.ModelAdmin):
    list_display = ['name', 'released', 'rating']
    list_filter = ('stores',)

@admin.register(Store)
class AdminStore(admin.ModelAdmin):
    list_display = ['id', 'name']

@admin.register(GamePrice)
class AdminGamePrice(admin.ModelAdmin):
    list_display = ['game', 'store', 'price', 'retail_price', 'savings', 'url']