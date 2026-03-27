import time
import requests
import os
from dotenv import load_dotenv
from django.core.management.base import BaseCommand
from catalog.models import Games, Ratings, Requirements, Store, Screenshots

load_dotenv()
API_KEY = os.getenv('API_KEY')

def time_counter(func):
    def wrapper(*args, **kwargs):
        now = time.time()
        result = func(*args, **kwargs)
        then = time.time()
        print(f"Выполнено за {then-now} секунд!")
        return result
    return wrapper

class Command(BaseCommand):
    @time_counter
    def handle(self, *args, **options):
        url = f'https://api.rawg.io/api/games?key={API_KEY}&page_size=40'
        games_fetched = 0
        max_games = 2000
        while url and games_fetched < max_games:
            response = requests.get(url)
            data = response.json()
            results = data['results']

            for result in results:

                game_obj, created = Games.objects.update_or_create(id=result['id'], defaults={
                    'slug': result['slug'],
                    'name': result['name'],
                    'released': result['released'],
                    'rating': result.get('rating', 0.0),
                    'rating_count': result.get('ratings_count', 0),
                    'description': fetch_description(result['id']),
                    'image': result['background_image']
                })

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

                game_obj.screenshots.all().delete()
                for screen in result.get('short_screenshots', []):
                    if screen['id'] != -1:
                        Screenshots.objects.create(game=game_obj, image=screen['image'])

                game_obj.requirements.all().delete()
                for platform_info in result.get('platforms', []):
                    platform = platform_info.get('platform')

                    reqs = platform_info.get('requirements_en') or {}
                    Requirements.objects.create(
                        game=game_obj,
                        platform_name=platform['name'],
                        minimum=reqs.get('minimum', ''),
                        recommended=reqs.get('recommended', ''))

                game_obj.detail_ratings.all().delete()
                ratings = result.get('ratings', [])
                for rating in ratings:
                    Ratings.objects.create(game=game_obj, title=rating['title'], count=rating['count'],
                                           percent=rating['percent'])

                games_fetched += 1
                if games_fetched > max_games:
                    break
            url = data.get('next')
        self.stdout.write(self.style.SUCCESS("Successfully completed!"))


def fetch_description(game_id):
    response = requests.get(f'https://api.rawg.io/api/games/{game_id}?key={API_KEY}')
    if response.status_code == 200:
        data = response.json()
        time.sleep(1)

        description = data.get('description', '')
    else: description = ''
    return description



# def test_data():
#     # url = f'https://api.rawg.io/api/games?key={API_KEY}&page_size=10'
#     url = f'https://api.rawg.io/api/games?key={API_KEY}&page_size=1'
#     response = requests.get(url)
#     data = response.json()
#     results = data['results'][0]
#     print(data)
#     print(results)
#     print(results.get('slug'))
#
# test_data()

