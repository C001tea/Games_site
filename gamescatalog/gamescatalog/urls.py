from django.contrib.sitemaps.views import sitemap
from catalog.sitemaps import GameSitemap
from django.contrib import admin
from django.urls import path, include

sitemaps = {
    'games': GameSitemap,
}

urlpatterns = [
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('admin-panel/', admin.site.urls),
    path('', include('catalog.urls')),
    path('accounts/', include('accounts.urls')),
    path('accounts/social/', include('allauth.urls')),
]

