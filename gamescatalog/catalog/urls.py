from . import views
from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('game/<slug:slug>/', views.game_detail, name='game'),
    path('platforms/', views.platforms, name="platforms"),
    path('genres/', views.genres, name="genres"),
    path('stores/', views.stores, name="stores"),
    path('games/', views.all_games, name="all_games"),
    path('about/', TemplateView.as_view(template_name='catalog/about.html'), name='about'),
    path('contact/', TemplateView.as_view(template_name='catalog/contact.html'), name='contact'),
    path('privacy/', TemplateView.as_view(template_name='catalog/privacy_policy.html'), name='privacy'),
    path('terms/', TemplateView.as_view(template_name='catalog/terms_&_conditions.html'), name='terms'),
    path('wishlist/', views.wishlist_page, name='wishlist'),
    path('wishlist/add/<int:game_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:game_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/set_notification/<int:game_id>/', views.set_notification, name='set_notification')
]