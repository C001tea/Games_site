import time
import requests
import os
from dotenv import load_dotenv
from django.core.management.base import BaseCommand
from catalog.models import Games, Ratings, Requirements, Store, Screenshots, GamePrice
import re

load_dotenv()
API_KEY = os.getenv('API_KEY')
shark_stores = {'1': 'Steam',
                '7': 'GOG',
                '25': 'Epic Games',
                }
#
# def time_counter(func):
#     def wrapper(*args, **kwargs):
#         now = time.time()
#         result = func(*args, **kwargs)
#         then = time.time()
#         print(f"Выполнено за {then-now} секунд!")
#         return result
#     return wrapper
#
# class Command(BaseCommand):
#
#     def add_arguments(self, parser):
#         parser.add_argument("--page", type=int, default=1, help='Стартовая страница')
#         parser.add_argument("--limit", type=int, default=2000, help='Сколько игр скачать')
#
#     @time_counter
#     def handle(self, *args, **options):
#
#         start_page = options['page']
#         max_games = options['limit']
#         games_fetched = 0
#
#         url = f'https://api.rawg.io/api/games?key={API_KEY}&page_size=40&page={start_page}'
#
#         while url and games_fetched < max_games:
#             self.stdout.write(f"Собираем данные о игре под номером {games_fetched}")
#             response = requests.get(url)
#             data = response.json()
#             results = data['results']
#
#             for result in results:
#
#                 game_obj, created = Games.objects.update_or_create(id=result['id'], defaults={
#                     'slug': result['slug'],
#                     'name': result['name'],
#                     'released': result['released'],
#                     'rating': result.get('rating', 0.0),
#                     'rating_count': result.get('ratings_count', 0),
#                     'description': fetch_description(result['id']),
#                     'image': result['background_image']
#                 })
#
#                 game_obj.stores.clear()
#                 for store_info in result.get('stores', []):
#                     store = store_info['store']
#                     store_obj, _ = Store.objects.get_or_create(
#                         id=store['id'],
#                         defaults={
#                             'name': store['name'],
#                             'domain': store['domain']
#                         })
#                     game_obj.stores.add(store_obj)
#
#                 game_obj.screenshots.all().delete()
#                 for screen in result.get('short_screenshots', []):
#                     if screen['id'] != -1:
#                         Screenshots.objects.create(game=game_obj, image=screen['image'])
#
#                 game_obj.requirements.all().delete()
#                 for platform_info in result.get('platforms', []):
#                     platform = platform_info.get('platform')
#
#                     reqs = platform_info.get('requirements_en') or {}
#                     Requirements.objects.create(
#                         game=game_obj,
#                         platform_name=platform['name'],
#                         minimum=reqs.get('minimum', ''),
#                         recommended=reqs.get('recommended', ''))
#
#                 game_obj.detail_ratings.all().delete()
#                 ratings = result.get('ratings', [])
#                 for rating in ratings:
#                     Ratings.objects.create(game=game_obj, title=rating['title'], count=rating['count'],
#                                            percent=rating['percent'])
#
#                 games_fetched += 1
#                 if games_fetched > max_games:
#                     break
#             url = data.get('next')
#         self.stdout.write(self.style.SUCCESS("Successfully completed!"))
#
#
def fetch_description(game_id):
    response = requests.get(f'https://api.rawg.io/api/games/{game_id}?key={API_KEY}')
    if response.status_code == 200:
        data = response.json()
        time.sleep(1)

        description = data.get('description', '')
    else: description = ''
    return description

def fetch_store_details(game_id):
    response = requests.get(f'https://api.rawg.io/api/games/{game_id}/stores?key={API_KEY}')
    data = response.json().get('results', [])
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
        max_games = 10
        url = f'https://api.rawg.io/api/games?key={API_KEY}&page_size=10'
        while url and games_fetched < max_games:
            response = requests.get(url)
            data = response.json()
            results = data['results']

            for result in results:
                game_id = result['id']
                store_details = fetch_store_details(game_id)
                steam_id = store_details['steam_id']
                game_obj, created = Games.objects.update_or_create(id=game_id, defaults={
                    'slug': result['slug'],
                    'name': result['name'],
                    'released': result['released'],
                    'rating': result.get('rating', 0.0),
                    'rating_count': result.get('ratings_count', 0),
                    'description': fetch_description(result['id']),
                    'image': result['background_image'],
                    'steam_id': steam_id
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
                    time.sleep(1)


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

                games_fetched += 1
                if games_fetched > max_games:
                    break
            url = data.get('next')
        self.stdout.write(self.style.SUCCESS("Successfully completed!"))