import time

import requests

API_KEY = '9a89219f39ec477b8c7c807b479d1536'


def time_counter(func):
    def wrapper():
        now = time.time()
        func()
        then = time.time()

        print(f"Выполнено за {then-now} секунд!")
    return wrapper

stores_list = []
screenshots_list = []
games_list = []
max_games = 100

@time_counter
def fetch_data():
    url = f'https://api.rawg.io/api/games?key={API_KEY}&page_size=40'
    games_fetched = 0
    while url and games_fetched < max_games:
        response = requests.get(url)
        data = response.json()
        results = data['results']

        for result in results:

            print(result)
            print(result['id'])
            print(result['slug'])
            print(result['name'])
            print(result['released'])
            print(result['background_image'])
            print(result['rating'])
            print(result['ratings'])

            for screen in result.get('short_screenshots', []):
                screenshots_list.append({
                    'games_id': result['id'],
                    'image': screen['image']
                })


            for store_info in result.get('stores', []):
                store = store_info['store']
                stores_list.append({
                    'game_id': result['id'],
                    'store_id': store['id'],
                    'name': store['name'],
                    'domain': store['domain']
                })


            games_list.append({
                'game_id': result['id'],
                'slug': result['slug'],
                'name': result['name'],
                'released': result['released'],
                'rating': result['rating'],
                'description': fetch_description(result['id']),
                'requirements': None
            })

            print(screenshots_list)
            print(stores_list)

        games_fetched += 1

        url = data.get('next')

# fetch_data()

def fetch_description(game_id):
    response = requests.get(f'https://api.rawg.io/api/games/{game_id}?key={API_KEY}')
    data = response.json()

    description = data['description']
    return description



def test_data():
    url = f'https://api.rawg.io/api/games?key={API_KEY}&page_size=10'

    response = requests.get(url)
    data = response.json()
    results = data['results']

    for result in results:
        print(result['id'], result['name'])

# test_data()


# What you need to do tomorrow:
# 1. finish to set all fetch: fetch requirements for table games, ratings;
# 2. renew tables in models and make migrations;
# 3. start developing front;
