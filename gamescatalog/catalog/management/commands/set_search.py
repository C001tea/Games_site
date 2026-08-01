from django.core.management.base import BaseCommand
from catalog.models import Game
import meilisearch
import requests

client = meilisearch.Client("http://localhost:7700", "artem")

def test():
    game = Game.objects.all().first()
    url = f'https://www.cheapshark.com/api/1.0/games?steamAppID={game.steam_id}'
    response = requests.get(url)
    print(response)

class Command(BaseCommand):
    def handle(self, *args, **options):
        # print(client.index("games").update_sortable_attributes(['added', 'rating']))

        games = Game.objects.all()
        documents = [
            {
                "id": game.id,
                "title": game.name,
                "added": game.added,
                "rating": float(game.rating) if game.rating else 0.0,
                "alternative_names": game.alternative_names
            }
            for game in games
        ]
        client.index('games').add_documents(documents)
