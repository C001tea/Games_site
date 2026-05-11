from django.core.management.base import BaseCommand
from catalog.models import Game
import meilisearch

client = meilisearch.Client("http://localhost:7700", "artem")

class Command(BaseCommand):
    def handle(self, *args, **options):
        print(client.index("games").update_sortable_attributes(['added', 'rating']))

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
