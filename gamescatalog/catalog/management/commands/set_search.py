from django.core.management.base import BaseCommand
from catalog.models import Game
import meilisearch
import requests
import time, os

client = meilisearch.Client("http://20.91.196.239:7700", os.getenv('MEILI_MASTER_KEY'))

def test():
    game = Game.objects.all().first()
    url = f'https://www.cheapshark.com/api/1.0/games?steamAppID={game.steam_id}'
    response = requests.get(url)
    print(response)

class Command(BaseCommand):
    def handle(self, *args, **options):
        # print(client.index("games").update_sortable_attributes(['added', 'rating']))

        games = Game.objects.all()
        batch_size = 200
        total = games.count()
        for i in range(0, total, batch_size):
            batch = games[i:i + batch_size]
            documents = [
                {
                    "id": game.id,
                    "title": game.name,
                    "added": game.added,
                    "rating": float(game.rating) if game.rating else 0.0,
                    "alternative_names": game.alternative_names
                }
                for game in batch
            ]
            client.index('games').add_documents(documents)
            self.stdout.write(f"Indexed {min(i + batch_size, total)}/{total}")
            time.sleep(2)