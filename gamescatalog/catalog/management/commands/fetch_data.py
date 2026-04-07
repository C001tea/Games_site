import time
import requests
import os
from dotenv import load_dotenv
from django.core.management.base import BaseCommand
from catalog.models import Game, Rating, Requirement, Store, Screenshot, GamePrice, Genre
import re

load_dotenv()
API_KEY = os.getenv('API_KEY')
shark_stores = {'1': 'Steam',
                '7': 'GOG',
                '25': 'Epic Games',
                }

def fetch_description(game_id):
    response = requests.get(f'https://api.rawg.io/api/games/{game_id}?key={API_KEY}')
    if response.status_code == 200:
        data = response.json()
        time.sleep(0.5)

        description = data.get('description', '')
    else: description = ''
    return description

def fetch_store_details(game_id):
    response = requests.get(f'https://api.rawg.io/api/games/{game_id}/stores?key={API_KEY}')
    print(response)
    if response.status_code == 200:
        data = response.json().get('results', [])
    else:
        data = []
    print(data)
    details = {'steam_id': None, 'urls': {}}
    for stores in data:
        store_id = stores.get('store_id')
        url = stores.get('url', '')
        details['urls'][store_id] = url
        if store_id == 1:
            match = re.search(r'/app/(\d+)', url)
            if match:
                details['steam_id'] = match.group(1)
    return details




class Command(BaseCommand):

    def handle(self, *args, **options):
        games_fetched = 0
        max_games = 2000
        start_page = 80
        url = f'https://api.rawg.io/api/games?key={API_KEY}&page_size=40'
        # url = f'https://api.rawg.io/api/games?key={API_KEY}&page_size=40&page={start_page}&ordering=-added'
        while url and games_fetched < max_games:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                results = data['results']
            else:
                continue
            for result in results:
                print(f"Собираются данные игры под номером {games_fetched+1}")
                game_id = result['id']
                store_details = fetch_store_details(game_id)
                steam_id = store_details['steam_id']
                genres = [genre.get('name') for genre in result.get('genres', [])]
                game_obj, created = Game.objects.update_or_create(id=game_id, defaults={
                    'slug': result['slug'],
                    'name': result['name'],
                    'released': result['released'],
                    'rating': result.get('rating', 0.0),
                    'rating_count': result.get('ratings_count', 0),
                    'description': fetch_description(result['id']),
                    'image': result['background_image'],
                    'steam_id': steam_id,
                })
                cheapshark_deals = {}

                if steam_id:
                    cs_response = requests.get(
                        f'https://www.cheapshark.com/api/1.0/games?steamAppID={steam_id}')
                    if cs_response.status_code == 200 and cs_response.json():
                        cs_game_id = cs_response.json()[0].get('gameID')
                        prices_response = requests.get(f'https://www.cheapshark.com/api/1.0/games?id={cs_game_id}')
                        if prices_response.status_code == 200:
                            for deal in prices_response.json().get('deals', []):
                                store_id = str(deal.get('storeID'))
                                if store_id in shark_stores:
                                    store_name = shark_stores[store_id]
                                    cheapshark_deals[store_name] = deal
                    time.sleep(0.5)


                game_obj.genres.clear()
                for g_name in genres:
                    genre_obj, _ = Genre.objects.get_or_create(name=g_name)

                    game_obj.genres.add(genre_obj)


                game_obj.stores.clear()
                for store_info in result.get('stores', []):
                    store = store_info['store']
                    store_obj, _ = Store.objects.get_or_create(
                        id=store['id'],
                        defaults={
                            'name': store['name'],
                            'domain': store['domain']
                        })
                    game_obj.stores.add(store_obj)

                    store_url = store_details['urls'].get(store['id'])

                    deal = cheapshark_deals.get(store['name'])
                    if deal:
                        GamePrice.objects.update_or_create(game=game_obj, store=store_obj, defaults={
                              'price': deal.get('price'),
                              'retail_price': deal.get('retailPrice'),
                              'savings': deal.get('savings'),
                              'url': store_url
                          })
                    else:
                        GamePrice.objects.update_or_create(game=game_obj, store=store_obj, defaults={
                              'price': None,
                              'retail_price': None,
                              'savings': None,
                              'url': store_url
                          })

                game_obj.screenshots.all().delete()
                for screen in result.get('short_screenshots', []):
                    if screen['id'] != -1:
                        Screenshot.objects.create(game=game_obj, image=screen['image'])

                game_obj.requirements.all().delete()
                for platform_info in result.get('platforms', []):
                    platform = platform_info.get('platform')

                    reqs = platform_info.get('requirements_en') or {}
                    Requirement.objects.create(
                        game=game_obj,
                        platform_name=platform['name'],
                        minimum=reqs.get('minimum', ''),
                        recommended=reqs.get('recommended', ''))

                game_obj.detail_ratings.all().delete()
                ratings = result.get('ratings', [])
                for rating in ratings:
                    Rating.objects.create(game=game_obj, title=rating['title'], count=rating['count'],
                                           percent=rating['percent'])

                games_fetched += 1
                if games_fetched > max_games:
                    break
            url = data.get('next')
        self.stdout.write(self.style.SUCCESS("Successfully completed!"))