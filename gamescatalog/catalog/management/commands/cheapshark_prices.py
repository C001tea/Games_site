from catalog.models import Game, Store, GamePrice
import requests
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
import traceback

shark_stores = [{"storeID":"1","storeName":"Steam","isActive":1,"images":{"banner":"/img/stores/banners/0.png","logo":"/img/stores/logos/0.png","icon":"/img/stores/icons/0.png"}},{"storeID":"2","storeName":"GamersGate","isActive":1,"images":{"banner":"/img/stores/banners/1.png","logo":"/img/stores/logos/1.png","icon":"/img/stores/icons/1.png"}},{"storeID":"3","storeName":"GreenManGaming","isActive":1,"images":{"banner":"/img/stores/banners/2.png","logo":"/img/stores/logos/2.png","icon":"/img/stores/icons/2.png"}},{"storeID":"4","storeName":"Amazon","isActive":0,"images":{"banner":"/img/stores/banners/3.png","logo":"/img/stores/logos/3.png","icon":"/img/stores/icons/3.png"}},{"storeID":"5","storeName":"GameStop","isActive":0,"images":{"banner":"/img/stores/banners/4.png","logo":"/img/stores/logos/4.png","icon":"/img/stores/icons/4.png"}},{"storeID":"6","storeName":"Direct2Drive","isActive":0,"images":{"banner":"/img/stores/banners/5.png","logo":"/img/stores/logos/5.png","icon":"/img/stores/icons/5.png"}},{"storeID":"7","storeName":"GOG","isActive":1,"images":{"banner":"/img/stores/banners/6.png","logo":"/img/stores/logos/6.png","icon":"/img/stores/icons/6.png"}},{"storeID":"8","storeName":"Origin","isActive":0,"images":{"banner":"/img/stores/banners/7.png","logo":"/img/stores/logos/7.png","icon":"/img/stores/icons/7.png"}},{"storeID":"9","storeName":"Get Games","isActive":0,"images":{"banner":"/img/stores/banners/8.png","logo":"/img/stores/logos/8.png","icon":"/img/stores/icons/8.png"}},{"storeID":"10","storeName":"Shiny Loot","isActive":0,"images":{"banner":"/img/stores/banners/9.png","logo":"/img/stores/logos/9.png","icon":"/img/stores/icons/9.png"}},{"storeID":"11","storeName":"Humble Store","isActive":1,"images":{"banner":"/img/stores/banners/10.png","logo":"/img/stores/logos/10.png","icon":"/img/stores/icons/10.png"}},{"storeID":"12","storeName":"Desura","isActive":0,"images":{"banner":"/img/stores/banners/11.png","logo":"/img/stores/logos/11.png","icon":"/img/stores/icons/11.png"}},{"storeID":"13","storeName":"Uplay","isActive":1,"images":{"banner":"/img/stores/banners/12.png","logo":"/img/stores/logos/12.png","icon":"/img/stores/icons/12.png"}},{"storeID":"14","storeName":"IndieGameStand","isActive":0,"images":{"banner":"/img/stores/banners/13.png","logo":"/img/stores/logos/13.png","icon":"/img/stores/icons/13.png"}},{"storeID":"15","storeName":"Fanatical","isActive":1,"images":{"banner":"/img/stores/banners/14.png","logo":"/img/stores/logos/14.png","icon":"/img/stores/icons/14.png"}},{"storeID":"16","storeName":"Gamesrocket","isActive":0,"images":{"banner":"/img/stores/banners/15.png","logo":"/img/stores/logos/15.png","icon":"/img/stores/icons/15.png"}},{"storeID":"17","storeName":"Games Republic","isActive":0,"images":{"banner":"/img/stores/banners/16.png","logo":"/img/stores/logos/16.png","icon":"/img/stores/icons/16.png"}},{"storeID":"18","storeName":"SilaGames","isActive":0,"images":{"banner":"/img/stores/banners/17.png","logo":"/img/stores/logos/17.png","icon":"/img/stores/icons/17.png"}},{"storeID":"19","storeName":"Playfield","isActive":0,"images":{"banner":"/img/stores/banners/18.png","logo":"/img/stores/logos/18.png","icon":"/img/stores/icons/18.png"}},{"storeID":"20","storeName":"ImperialGames","isActive":0,"images":{"banner":"/img/stores/banners/19.png","logo":"/img/stores/logos/19.png","icon":"/img/stores/icons/19.png"}},{"storeID":"21","storeName":"WinGameStore","isActive":1,"images":{"banner":"/img/stores/banners/20.png","logo":"/img/stores/logos/20.png","icon":"/img/stores/icons/20.png"}},{"storeID":"22","storeName":"FunStockDigital","isActive":0,"images":{"banner":"/img/stores/banners/21.png","logo":"/img/stores/logos/21.png","icon":"/img/stores/icons/21.png"}},{"storeID":"23","storeName":"GameBillet","isActive":1,"images":{"banner":"/img/stores/banners/22.png","logo":"/img/stores/logos/22.png","icon":"/img/stores/icons/22.png"}},{"storeID":"24","storeName":"Voidu","isActive":0,"images":{"banner":"/img/stores/banners/23.png","logo":"/img/stores/logos/23.png","icon":"/img/stores/icons/23.png"}},{"storeID":"25","storeName":"Epic Games Store","isActive":1,"images":{"banner":"/img/stores/banners/24.png","logo":"/img/stores/logos/24.png","icon":"/img/stores/icons/24.png"}},{"storeID":"26","storeName":"Razer Game Store","isActive":0,"images":{"banner":"/img/stores/banners/25.png","logo":"/img/stores/logos/25.png","icon":"/img/stores/icons/25.png"}},{"storeID":"27","storeName":"Gamesplanet","isActive":1,"images":{"banner":"/img/stores/banners/26.png","logo":"/img/stores/logos/26.png","icon":"/img/stores/icons/26.png"}},{"storeID":"28","storeName":"Gamesload","isActive":1,"images":{"banner":"/img/stores/banners/27.png","logo":"/img/stores/logos/27.png","icon":"/img/stores/icons/27.png"}},{"storeID":"29","storeName":"2Game","isActive":1,"images":{"banner":"/img/stores/banners/28.png","logo":"/img/stores/logos/28.png","icon":"/img/stores/icons/28.png"}},{"storeID":"30","storeName":"IndieGala","isActive":1,"images":{"banner":"/img/stores/banners/29.png","logo":"/img/stores/logos/29.png","icon":"/img/stores/icons/29.png"}},{"storeID":"31","storeName":"Blizzard Shop","isActive":0,"images":{"banner":"/img/stores/banners/30.png","logo":"/img/stores/logos/30.png","icon":"/img/stores/icons/30.png"}},{"storeID":"32","storeName":"AllYouPlay","isActive":0,"images":{"banner":"/img/stores/banners/31.png","logo":"/img/stores/logos/31.png","icon":"/img/stores/icons/31.png"}},{"storeID":"33","storeName":"DLGamer","isActive":0,"images":{"banner":"/img/stores/banners/32.png","logo":"/img/stores/logos/32.png","icon":"/img/stores/icons/32.png"}},{"storeID":"34","storeName":"Noctre","isActive":0,"images":{"banner":"/img/stores/banners/33.png","logo":"/img/stores/logos/33.png","icon":"/img/stores/icons/33.png"}},{"storeID":"35","storeName":"DreamGame","isActive":1,"images":{"banner":"/img/stores/banners/34.png","logo":"/img/stores/logos/34.png","icon":"/img/stores/icons/34.png"}}]

store_domains = {
    '1': 'store.steampowered.com',
    '2': 'www.gamersgate.com',
    '3': 'www.greenmangaming.com',
    '7': 'www.gog.com',
    '11': 'www.humblebundle.com',
    '13': 'www.ubisoft.com',
    '15': 'www.fanatical.com',
    '21': 'www.wingamestore.com',
    '23': 'www.gamebillet.com',
    '25': 'store.epicgames.com',
    '27': 'www.gamesplanet.com',
    '28': 'www.gamesload.com',
    '29': 'www.2game.com',
    '30': 'www.indiegala.com',
    '35': 'www.dreamgame.com',
}

class Command(BaseCommand):
    def handle(self, *args, **options):

        log_message = list()
        log_message.append("Starting collect weekly update!!!")
        try:

            for i, game in enumerate(Game.objects.all(), 1):
                print(f"Game №{i}")
                if game.steam_id:
                    steam_id = game.steam_id
                    url = f'https://www.cheapshark.com/api/1.0/games?steamAppID={steam_id}'
                    response = requests.get(url)
                    if response.status_code == 200 and response.json():

                        cs_game_id = response.json()[0].get('gameID')
                        prices_response = requests.get(f'https://www.cheapshark.com/api/1.0/games?id={cs_game_id}')
                        if prices_response.status_code == 200:

                            for deal in prices_response.json().get('deals', []):
                                print(deal)
                                store_id = str(deal.get('storeID'))
                                sh_store = None
                                for store in shark_stores:
                                    if store.get("storeID") == store_id:
                                        sh_store = store
                                        break
                                deal_url = f'https://www.cheapshark.com/redirect?dealID={deal["dealID"]}'

                                store_obj, _ = Store.objects.get_or_create(
                                    id=int(sh_store.get('storeID')),
                                    defaults={
                                        'name': sh_store.get('storeName'),
                                        'domain': store_domains.get(sh_store.get('storeID'))
                                    }
                                )

                                GamePrice.objects.update_or_create(
                                    game=game,
                                    store=store_obj,
                                    defaults={
                                        'price': deal.get('price'),
                                        'retail_price': deal.get('retailPrice'),
                                        'savings': deal.get('savings'),
                                        'url': deal_url
                                    }
                                )
            log_message.append("Successfully updated all 8142 games!!!")

            send_mail(
                'GameVault: parser did great job!',
                "\n".join(log_message),
                'artemgrecu6@gmail.com',
                ['artemgrecu6@gmail.com'],
                fail_silently=False
            )
        except Exception as e:
            error_message = traceback.format_exc()
            log_message.append(f"\nFailed :( \n{error_message}")
            send_mail(
                'GameVault: parses failed, what a pity!',
                "\n".join(log_message),
                'artemgrecu6@gmail.com',
                ['artemgrecu6@gmail.com'],
                fail_silently=False
            )