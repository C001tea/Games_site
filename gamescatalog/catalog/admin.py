from django.contrib import admin
from .models import Games, Store, Ratings, Requirements, Screenshots


@admin.register(Games)
class AdminGame(admin.ModelAdmin):
    list_display = ['name', 'released', 'rating']