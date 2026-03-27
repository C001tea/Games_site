from django.contrib import admin
from .models import Games, Store, Ratings, Requirements, Screenshots

admin.site.register([Screenshots, Games, Store, Ratings, Requirements])


