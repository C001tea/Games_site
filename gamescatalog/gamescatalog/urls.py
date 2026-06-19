from django.contrib.sitemaps.views import sitemap
from catalog.sitemaps import GameSitemap
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

sitemaps = {
    'games': GameSitemap,
}

urlpatterns = [
        path('robots.txt', TemplateView.as_view(
        template_name='robots.txt',
        content_type='text/plain'
    )),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('admin-panel/', admin.site.urls),
    path('', include('catalog.urls')),
    path('accounts/', include('accounts.urls')),
    path('accounts/social/', include('allauth.urls')),
]