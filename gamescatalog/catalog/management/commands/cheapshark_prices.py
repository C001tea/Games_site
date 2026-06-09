from catalog.models import Game, Store, GamePrice, PriceHistory
import requests
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
import traceback
from decimal import Decimal
from django.core.paginator import Paginator
import time

shark_stores = {
    "1": {"storeID": "1", "storeName": "Steam"},
    "2": {"storeID": "2", "storeName": "GamersGate"},
    "3": {"storeID": "3", "storeName": "GreenManGaming"},
    "4": {"storeID": "4", "storeName": "Amazon"},
    "5": {"storeID": "5", "storeName": "GameStop"},
    "6": {"storeID": "6", "storeName": "Direct2Drive"},
    "7": {"storeID": "7", "storeName": "GOG"},
    "8": {"storeID": "8", "storeName": "Origin"},
    "9": {"storeID": "9", "storeName": "Get Games"},
    "10": {"storeID": "10", "storeName": "Shiny Loot"},
    "11": {"storeID": "11", "storeName": "Humble Store"},
    "12": {"storeID": "12", "storeName": "Desura"},
    "13": {"storeID": "13", "storeName": "Uplay"},
    "14": {"storeID": "14", "storeName": "IndieGameStand"},
    "15": {"storeID": "15", "storeName": "Fanatical"},
    "16": {"storeID": "16", "storeName": "Gamesrocket"},
    "17": {"storeID": "17", "storeName": "Games Republic"},
    "18": {"storeID": "18", "storeName": "SilaGames"},
    "19": {"storeID": "19", "storeName": "Playfield"},
    "20": {"storeID": "20", "storeName": "ImperialGames"},
    "21": {"storeID": "21", "storeName": "WinGameStore"},
    "22": {"storeID": "22", "storeName": "FunStockDigital"},
    "23": {"storeID": "23", "storeName": "GameBillet"},
    "24": {"storeID": "24", "storeName": "Voidu"},
    "25": {"storeID": "25", "storeName": "Epic Games Store"},
    "26": {"storeID": "26", "storeName": "Razer Game Store"},
    "27": {"storeID": "27", "storeName": "Gamesplanet"},
    "28": {"storeID": "28", "storeName": "Gamesload"},
    "29": {"storeID": "29", "storeName": "2Game"},
    "30": {"storeID": "30", "storeName": "IndieGala"},
    "31": {"storeID": "31", "storeName": "Blizzard Shop"},
    "32": {"storeID": "32", "storeName": "AllYouPlay"},
    "33": {"storeID": "33", "storeName": "DLGamer"},
    "34": {"storeID": "34", "storeName": "Noctre"},
    "35": {"storeID": "35", "storeName": "DreamGame"},
}

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

            stores_cache = {store.id: store for store in Store.objects.all()}
            paginator = Paginator(Game.objects.prefetch_related('prices').all().order_by('id'), 100)

            for page in paginator.page_range:
                games = paginator.page(page).object_list

                game_prices_cache = {
                    game.id: {gp.store_id: gp for gp in game.prices.all()} for game in games
                }

                history_to_create = []
                prices_to_create = []
                prices_to_update = []

                for i, game in enumerate(games, 1):
                    print(f"Game №{i}")

                    if not game.steam_id:
                        continue

                    url = f'https://www.cheapshark.com/api/1.0/games?steamAppID={game.steam_id}'
                    response = requests.get(url)
                    if response.status_code != 200 or not response.json():
                        continue

                    time.sleep(0.3)

                    cs_game_id = response.json()[0].get('gameID')
                    prices_response = requests.get(f'https://www.cheapshark.com/api/1.0/games?id={cs_game_id}')
                    if prices_response.status_code != 200:
                        continue

                    time.sleep(0.3)

                    current_price = game_prices_cache.get(game.id, {})

                    for deal in prices_response.json().get('deals', []):
                        print('+++', deal)

                        store_id = str(deal.get('storeID'))

                        sh_store = shark_stores.get(store_id)

                        if not sh_store:
                            continue

                        store_obj = stores_cache.get(int(store_id))

                        if not store_obj:
                            store_obj, _ = Store.objects.get_or_create(
                                id=int(sh_store.get('storeID')),
                                defaults={
                                    'name': sh_store.get('storeName'),
                                    'domain': store_domains.get(sh_store.get('storeID'))
                                }
                            )
                            stores_cache[int(store_id)] = store_obj

                        deal_url = f'https://www.cheapshark.com/redirect?dealID={deal["dealID"]}'
                        time.sleep(0.3)

                        game_price = current_price.get(int(store_id))

                        new_price = Decimal(deal.get('price'))

                        if game_price is None or game_price.price is None:
                            print("first note of this game price")

                            history_to_create.append(PriceHistory(
                                game=game,
                                store=store_obj,
                                price=new_price
                            ))
                        elif game_price.price != new_price:

                            history_to_create.append(PriceHistory(
                                game=game,
                                store=store_obj,
                                price=new_price
                            ))

                        else:
                            print("Without changes")


                        if game_price is None:
                            prices_to_create.append(GamePrice(
                                    game=game,
                                    store=store_obj,
                                    price=deal.get('price'),
                                    retail_price=deal.get('retailPrice'),
                                    savings=deal.get('savings'),
                                    url=deal_url
                                ))
                        else:
                            game_price.price = deal.get('price')
                            game_price.retail_price = deal.get('retailPrice')
                            game_price.savings = deal.get('savings')
                            game_price.url = deal_url
                            prices_to_update.append(game_price)

                if prices_to_update:
                    GamePrice.objects.bulk_update(prices_to_update, fields=['price', 'retail_price', 'savings', 'url'])

                if prices_to_create:
                    GamePrice.objects.bulk_create(prices_to_create, ignore_conflicts=True)

                if history_to_create:
                    PriceHistory.objects.bulk_create(history_to_create)

            log_message.append("Successfully updated all 8142 games!!!")

            send_mail(
                'GameVault: parser did great job!',
                "\n".join(log_message),
                'artemgrecu6@gmail.com',
                ['artemgrecu6@gmail.com'],
                fail_silently=False
            )
        except Exception:
            error_message = traceback.format_exc()
            log_message.append(f"\nFailed :( \n{error_message}")
            send_mail(
                'GameVault: parses failed, what a pity!',
                "\n".join(log_message),
                'artemgrecu6@gmail.com',
                ['artemgrecu6@gmail.com'],
                fail_silently=False
            )