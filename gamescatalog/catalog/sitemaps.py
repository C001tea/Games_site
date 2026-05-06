from django.contrib.sitemaps import Sitemap
from .models import Game

class GameSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Game.objects.all()

    def location(self, item):
        return f'/game/{item.slug}/'