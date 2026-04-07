from . import views
from django.urls import path

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('game/<slug:slug>', views.game_detail, name='game'),
    path('platforms', views.platforms, name="platforms"),
]