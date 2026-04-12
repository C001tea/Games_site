import time
import requests
import os
from dotenv import load_dotenv
from django.core.management.base import BaseCommand
from catalog.models import Game, Rating, Requirement, Store, Screenshot, GamePrice, Genre
import re

load_dotenv()
API_KEY = os.getenv('API_KEY')

rawg_stores_to_cheap_shark = {
    'Epic Games': 'Epic Games Store',
    'Ubisoft Store': 'Uplay',
    'EA App': 'Origin',
}

shark_stores = [{"storeID":"1","storeName":"Steam","isActive":1,"images":{"banner":"/img/stores/banners/0.png","logo":"/img/stores/logos/0.png","icon":"/img/stores/icons/0.png"}},{"storeID":"2","storeName":"GamersGate","isActive":1,"images":{"banner":"/img/stores/banners/1.png","logo":"/img/stores/logos/1.png","icon":"/img/stores/icons/1.png"}},{"storeID":"3","storeName":"GreenManGaming","isActive":1,"images":{"banner":"/img/stores/banners/2.png","logo":"/img/stores/logos/2.png","icon":"/img/stores/icons/2.png"}},{"storeID":"4","storeName":"Amazon","isActive":0,"images":{"banner":"/img/stores/banners/3.png","logo":"/img/stores/logos/3.png","icon":"/img/stores/icons/3.png"}},{"storeID":"5","storeName":"GameStop","isActive":0,"images":{"banner":"/img/stores/banners/4.png","logo":"/img/stores/logos/4.png","icon":"/img/stores/icons/4.png"}},{"storeID":"6","storeName":"Direct2Drive","isActive":0,"images":{"banner":"/img/stores/banners/5.png","logo":"/img/stores/logos/5.png","icon":"/img/stores/icons/5.png"}},{"storeID":"7","storeName":"GOG","isActive":1,"images":{"banner":"/img/stores/banners/6.png","logo":"/img/stores/logos/6.png","icon":"/img/stores/icons/6.png"}},{"storeID":"8","storeName":"Origin","isActive":0,"images":{"banner":"/img/stores/banners/7.png","logo":"/img/stores/logos/7.png","icon":"/img/stores/icons/7.png"}},{"storeID":"9","storeName":"Get Games","isActive":0,"images":{"banner":"/img/stores/banners/8.png","logo":"/img/stores/logos/8.png","icon":"/img/stores/icons/8.png"}},{"storeID":"10","storeName":"Shiny Loot","isActive":0,"images":{"banner":"/img/stores/banners/9.png","logo":"/img/stores/logos/9.png","icon":"/img/stores/icons/9.png"}},{"storeID":"11","storeName":"Humble Store","isActive":1,"images":{"banner":"/img/stores/banners/10.png","logo":"/img/stores/logos/10.png","icon":"/img/stores/icons/10.png"}},{"storeID":"12","storeName":"Desura","isActive":0,"images":{"banner":"/img/stores/banners/11.png","logo":"/img/stores/logos/11.png","icon":"/img/stores/icons/11.png"}},{"storeID":"13","storeName":"Uplay","isActive":1,"images":{"banner":"/img/stores/banners/12.png","logo":"/img/stores/logos/12.png","icon":"/img/stores/icons/12.png"}},{"storeID":"14","storeName":"IndieGameStand","isActive":0,"images":{"banner":"/img/stores/banners/13.png","logo":"/img/stores/logos/13.png","icon":"/img/stores/icons/13.png"}},{"storeID":"15","storeName":"Fanatical","isActive":1,"images":{"banner":"/img/stores/banners/14.png","logo":"/img/stores/logos/14.png","icon":"/img/stores/icons/14.png"}},{"storeID":"16","storeName":"Gamesrocket","isActive":0,"images":{"banner":"/img/stores/banners/15.png","logo":"/img/stores/logos/15.png","icon":"/img/stores/icons/15.png"}},{"storeID":"17","storeName":"Games Republic","isActive":0,"images":{"banner":"/img/stores/banners/16.png","logo":"/img/stores/logos/16.png","icon":"/img/stores/icons/16.png"}},{"storeID":"18","storeName":"SilaGames","isActive":0,"images":{"banner":"/img/stores/banners/17.png","logo":"/img/stores/logos/17.png","icon":"/img/stores/icons/17.png"}},{"storeID":"19","storeName":"Playfield","isActive":0,"images":{"banner":"/img/stores/banners/18.png","logo":"/img/stores/logos/18.png","icon":"/img/stores/icons/18.png"}},{"storeID":"20","storeName":"ImperialGames","isActive":0,"images":{"banner":"/img/stores/banners/19.png","logo":"/img/stores/logos/19.png","icon":"/img/stores/icons/19.png"}},{"storeID":"21","storeName":"WinGameStore","isActive":1,"images":{"banner":"/img/stores/banners/20.png","logo":"/img/stores/logos/20.png","icon":"/img/stores/icons/20.png"}},{"storeID":"22","storeName":"FunStockDigital","isActive":0,"images":{"banner":"/img/stores/banners/21.png","logo":"/img/stores/logos/21.png","icon":"/img/stores/icons/21.png"}},{"storeID":"23","storeName":"GameBillet","isActive":1,"images":{"banner":"/img/stores/banners/22.png","logo":"/img/stores/logos/22.png","icon":"/img/stores/icons/22.png"}},{"storeID":"24","storeName":"Voidu","isActive":0,"images":{"banner":"/img/stores/banners/23.png","logo":"/img/stores/logos/23.png","icon":"/img/stores/icons/23.png"}},{"storeID":"25","storeName":"Epic Games Store","isActive":1,"images":{"banner":"/img/stores/banners/24.png","logo":"/img/stores/logos/24.png","icon":"/img/stores/icons/24.png"}},{"storeID":"26","storeName":"Razer Game Store","isActive":0,"images":{"banner":"/img/stores/banners/25.png","logo":"/img/stores/logos/25.png","icon":"/img/stores/icons/25.png"}},{"storeID":"27","storeName":"Gamesplanet","isActive":1,"images":{"banner":"/img/stores/banners/26.png","logo":"/img/stores/logos/26.png","icon":"/img/stores/icons/26.png"}},{"storeID":"28","storeName":"Gamesload","isActive":1,"images":{"banner":"/img/stores/banners/27.png","logo":"/img/stores/logos/27.png","icon":"/img/stores/icons/27.png"}},{"storeID":"29","storeName":"2Game","isActive":1,"images":{"banner":"/img/stores/banners/28.png","logo":"/img/stores/logos/28.png","icon":"/img/stores/icons/28.png"}},{"storeID":"30","storeName":"IndieGala","isActive":1,"images":{"banner":"/img/stores/banners/29.png","logo":"/img/stores/logos/29.png","icon":"/img/stores/icons/29.png"}},{"storeID":"31","storeName":"Blizzard Shop","isActive":0,"images":{"banner":"/img/stores/banners/30.png","logo":"/img/stores/logos/30.png","icon":"/img/stores/icons/30.png"}},{"storeID":"32","storeName":"AllYouPlay","isActive":0,"images":{"banner":"/img/stores/banners/31.png","logo":"/img/stores/logos/31.png","icon":"/img/stores/icons/31.png"}},{"storeID":"33","storeName":"DLGamer","isActive":0,"images":{"banner":"/img/stores/banners/32.png","logo":"/img/stores/logos/32.png","icon":"/img/stores/icons/32.png"}},{"storeID":"34","storeName":"Noctre","isActive":0,"images":{"banner":"/img/stores/banners/33.png","logo":"/img/stores/logos/33.png","icon":"/img/stores/icons/33.png"}},{"storeID":"35","storeName":"DreamGame","isActive":1,"images":{"banner":"/img/stores/banners/34.png","logo":"/img/stores/logos/34.png","icon":"/img/stores/icons/34.png"}}]
rawg_stores = {"count":10,"next":None,"previous":None,"results":[{"id":1,"name":"Steam","domain":"store.steampowered.com","slug":"steam","games_count":123294,"image_background":"https://media.rawg.io/media/games/26d/26d4437715bee60138dab4a7c8c59c92.jpg","games":[{"id":3498,"slug":"grand-theft-auto-v","name":"Grand Theft Auto V","added":22549},{"id":3328,"slug":"the-witcher-3-wild-hunt","name":"The Witcher 3: Wild Hunt","added":22188},{"id":4200,"slug":"portal-2","name":"Portal 2","added":20875},{"id":4291,"slug":"counter-strike-global-offensive","name":"Counter-Strike: Global Offensive","added":18357},{"id":5286,"slug":"tomb-raider","name":"Tomb Raider (2013)","added":17808},{"id":13536,"slug":"portal","name":"Portal","added":17797}]},{"id":3,"name":"PlayStation Store","domain":"store.playstation.com","slug":"playstation-store","games_count":8075,"image_background":"https://media.rawg.io/media/games/021/021c4e21a1824d2526f925eff6324653.jpg","games":[{"id":3498,"slug":"grand-theft-auto-v","name":"Grand Theft Auto V","added":22549},{"id":3328,"slug":"the-witcher-3-wild-hunt","name":"The Witcher 3: Wild Hunt","added":22188},{"id":4200,"slug":"portal-2","name":"Portal 2","added":20875},{"id":4291,"slug":"counter-strike-global-offensive","name":"Counter-Strike: Global Offensive","added":18357},{"id":5286,"slug":"tomb-raider","name":"Tomb Raider (2013)","added":17808},{"id":5679,"slug":"the-elder-scrolls-v-skyrim","name":"The Elder Scrolls V: Skyrim","added":16854}]},{"id":2,"name":"Xbox Store","domain":"microsoft.com","slug":"xbox-store","games_count":4938,"image_background":"https://media.rawg.io/media/games/34b/34b1f1850a1c06fd971bc6ab3ac0ce0e.jpg","games":[{"id":3498,"slug":"grand-theft-auto-v","name":"Grand Theft Auto V","added":22549},{"id":3328,"slug":"the-witcher-3-wild-hunt","name":"The Witcher 3: Wild Hunt","added":22188},{"id":4200,"slug":"portal-2","name":"Portal 2","added":20875},{"id":28,"slug":"red-dead-redemption-2","name":"Red Dead Redemption 2","added":16852},{"id":4062,"slug":"bioshock-infinite","name":"BioShock Infinite","added":16105},{"id":802,"slug":"borderlands-2","name":"Borderlands 2","added":16011}]},{"id":4,"name":"App Store","domain":"apps.apple.com","slug":"apple-appstore","games_count":75590,"image_background":"https://media.rawg.io/media/games/13a/13a528ac9cf48bbb6be5d35fe029336d.jpg","games":[{"id":5286,"slug":"tomb-raider","name":"Tomb Raider (2013)","added":17808},{"id":4062,"slug":"bioshock-infinite","name":"BioShock Infinite","added":16105},{"id":802,"slug":"borderlands-2","name":"Borderlands 2","added":16011},{"id":3439,"slug":"life-is-strange-episode-1-2","name":"Life is Strange","added":15904},{"id":4286,"slug":"bioshock","name":"BioShock","added":14765},{"id":1030,"slug":"limbo","name":"Limbo","added":14146}]},{"id":5,"name":"GOG","domain":"gog.com","slug":"gog","games_count":7244,"image_background":"https://media.rawg.io/media/games/587/587588c64afbff80e6f444eb2e46f9da.jpg","games":[{"id":3328,"slug":"the-witcher-3-wild-hunt","name":"The Witcher 3: Wild Hunt","added":22188},{"id":3439,"slug":"life-is-strange-episode-1-2","name":"Life is Strange","added":15904},{"id":58175,"slug":"god-of-war-2","name":"God of War (2018)","added":14544},{"id":1030,"slug":"limbo","name":"Limbo","added":14146},{"id":2454,"slug":"doom","name":"DOOM (2016)","added":14019},{"id":41494,"slug":"cyberpunk-2077","name":"Cyberpunk 2077","added":13950}]},{"id":6,"name":"Nintendo Store","domain":"nintendo.com","slug":"nintendo","games_count":9150,"image_background":"https://media.rawg.io/media/games/be0/be01c3d7d8795a45615da139322ca080.jpg","games":[{"id":3328,"slug":"the-witcher-3-wild-hunt","name":"The Witcher 3: Wild Hunt","added":22188},{"id":5679,"slug":"the-elder-scrolls-v-skyrim","name":"The Elder Scrolls V: Skyrim","added":16854},{"id":4062,"slug":"bioshock-infinite","name":"BioShock Infinite","added":16105},{"id":1030,"slug":"limbo","name":"Limbo","added":14146},{"id":3939,"slug":"payday-2","name":"PAYDAY 2","added":14142},{"id":2454,"slug":"doom","name":"DOOM (2016)","added":14019}]},{"id":7,"name":"Xbox 360 Store","domain":"marketplace.xbox.com","slug":"xbox360","games_count":1915,"image_background":"https://media.rawg.io/media/games/bc0/bc06a29ceac58652b684deefe7d56099.jpg","games":[{"id":3498,"slug":"grand-theft-auto-v","name":"Grand Theft Auto V","added":22549},{"id":4200,"slug":"portal-2","name":"Portal 2","added":20875},{"id":4291,"slug":"counter-strike-global-offensive","name":"Counter-Strike: Global Offensive","added":18357},{"id":5286,"slug":"tomb-raider","name":"Tomb Raider (2013)","added":17808},{"id":12020,"slug":"left-4-dead-2","name":"Left 4 Dead 2","added":17502},{"id":5679,"slug":"the-elder-scrolls-v-skyrim","name":"The Elder Scrolls V: Skyrim","added":16854}]},{"id":8,"name":"Google Play","domain":"play.google.com","slug":"google-play","games_count":17126,"image_background":"https://media.rawg.io/media/games/9fa/9fa63622543e5d4f6d99aa9d73b043de.jpg","games":[{"id":5286,"slug":"tomb-raider","name":"Tomb Raider (2013)","added":17808},{"id":13536,"slug":"portal","name":"Portal","added":17797},{"id":13537,"slug":"half-life-2","name":"Half-Life 2","added":16098},{"id":802,"slug":"borderlands-2","name":"Borderlands 2","added":16011},{"id":3439,"slug":"life-is-strange-episode-1-2","name":"Life is Strange","added":15904},{"id":1030,"slug":"limbo","name":"Limbo","added":14146}]},{"id":9,"name":"itch.io","domain":"itch.io","slug":"itch","games_count":654200,"image_background":"https://media.rawg.io/media/games/e63/e635b8c7fbe3ffd69ad6c1c586cd250e.jpg","games":[{"id":613,"slug":"bastion","name":"Bastion","added":8753},{"id":5525,"slug":"brutal-legend","name":"Brutal Legend","added":8422},{"id":356714,"slug":"among-us","name":"Among Us","added":7948},{"id":1010,"slug":"transistor","name":"Transistor","added":7835},{"id":11726,"slug":"dead-cells","name":"Dead Cells","added":7294},{"id":1358,"slug":"papers-please","name":"Papers, Please","added":7259}]},{"id":11,"name":"Epic Games","domain":"epicgames.com","slug":"epic-games","games_count":1451,"image_background":"https://media.rawg.io/media/games/1bd/1bd2657b81eb0c99338120ad444b24ff.jpg","games":[{"id":3498,"slug":"grand-theft-auto-v","name":"Grand Theft Auto V","added":22549},{"id":5286,"slug":"tomb-raider","name":"Tomb Raider (2013)","added":17808},{"id":28,"slug":"red-dead-redemption-2","name":"Red Dead Redemption 2","added":16852},{"id":4062,"slug":"bioshock-infinite","name":"BioShock Infinite","added":16105},{"id":32,"slug":"destiny-2","name":"Destiny 2","added":14583},{"id":58175,"slug":"god-of-war-2","name":"God of War (2018)","added":14544}]}]}

def fetch_description(game_id):
    response = requests.get(f'https://api.rawg.io/api/games/{game_id}?key={API_KEY}')
    if response.status_code == 200:
        data = response.json()
        time.sleep(0.5)
        alternative_names = data.get('alternative_names', '')
        developers = data.get('developers', '')[0]['name']
        description = data.get('description', '')
    else:
        description = ''
        developers = ''
        alternative_names = []
    desc_dev = {'description': description, 'developers': developers, 'alternative_names': alternative_names}
    return desc_dev

def fetch_store_details(game_id):
    response = requests.get(f'https://api.rawg.io/api/games/{game_id}/stores?key={API_KEY}')
    if response.status_code == 200:
        data = response.json().get('results', [])
    else:
        data = []
    details = {'steam_id': None, 'urls': {}}
    for stores in data:
        print(stores)
        store_id = stores.get('store_id')
        url = stores.get('url', '')
        details['urls'][store_id] = url
        if store_id == 1:
            match = re.search(r'/app/(\d+)', url)
            if match:
                details['steam_id'] = match.group(1)
    return details


def test():
    steam_id = 1687950
    cs_response = requests.get(
        f'https://www.cheapshark.com/api/1.0/games?steamAppID={steam_id}')
    print(cs_response.json())
    if cs_response.status_code == 200 and cs_response.json():
        cs_game_id = cs_response.json()[0].get('gameID')
        prices_response = requests.get(f'https://www.cheapshark.com/api/1.0/games?id={cs_game_id}')
        print(prices_response.json())

class Command(BaseCommand):

    def handle(self, *args, **options):
        games_fetched = 0
        max_games = 2
        start_page = 80
        url = f'https://api.rawg.io/api/games?key={API_KEY}&page_size=1'
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
                fetch_info = fetch_description(result['id'])
                game_obj, created = Game.objects.update_or_create(id=game_id, defaults={
                    'slug': result['slug'],
                    'name': result['name'],
                    'released': result['released'],
                    'rating': result.get('rating', 0.0),
                    'rating_count': result.get('ratings_count', 0),
                    'description': fetch_info['description'],
                    'image': result['background_image'],
                    'steam_id': steam_id,
                    'developers': fetch_info['developers'],
                    'alternative_names': fetch_info['alternative_names']
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
                                for shark_store in shark_stores:
                                    if shark_store.get("storeID") == store_id:
                                        store_name = shark_store.get('storeName')
                                        cheapshark_deals[store_name] = deal
                                        break
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
                    print("\n\n\n\nstore", store)

                    cheap_shark_names = rawg_stores_to_cheap_shark.get(store['name'], store['name'])

                    deal = cheapshark_deals.get(cheap_shark_names)
                    print("deal", deal)
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