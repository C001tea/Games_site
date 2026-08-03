from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.text import slugify
import meilisearch, os
from django.db.models import Min, Max
from django.contrib.staticfiles import finders
from datetime import date
from django.urls import reverse
from accounts.models import User

client = meilisearch.Client("http://20.91.196.239:7700", os.getenv('MEILI_MASTER_KEY'))

class Store(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name="Name")
    domain = models.CharField(max_length=150, verbose_name="domain")

    icons = {
        "store.steampowered.com": "steam",
        "epicgames.com": "epicgames",
        "store.playstation.com": "playstation",
        "apps.apple.com": "appstore",
        "nintendo.com": "nintendo",
        "itch.io": "itch",
        "play.google.com": "googleplay",
        "marketplace.xbox.com": "xbox360",
        "gog.com": "gog",
        "microsoft.com": "xbox",
    }

    def __str__(self):
        return self.name

    @property
    def clean_slug(self):
        return self.icons.get(self.domain)

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class Platform(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    url = models.URLField(max_length=1000, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    @property
    def has_icon(self):

        path = f"catalog/icons/platforms/{self.slug}.svg"

        if finders.find(path):
            return True
        return False

    def __str__(self):
        return self.name

class Tag(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=300, null=True, blank=True)
    slug = models.CharField(max_length=300, null=True, blank=True)

    def __str__(self):
        return self.name

class Game(models.Model):
    id = models.IntegerField(primary_key=True)
    slug = models.SlugField(max_length=255, unique=True)
    name = models.CharField(max_length=255, verbose_name="Name")
    released = models.DateField(null=True, blank=True, verbose_name="released")
    rating = models.FloatField(default=0.0, verbose_name="rating")
    rating_count = models.IntegerField(default=0, verbose_name="Ratings count")
    image = models.URLField(max_length=500, null=True, blank=True, verbose_name="image")
    description = models.TextField(null=True, blank=True, verbose_name="Description")
    steam_id = models.CharField(null=True, blank=True)
    alternative_names = models.JSONField(default=list, null=True, blank=True)
    developers = models.CharField(max_length=200, null=True, blank=True)
    added = models.IntegerField(null=True, blank=True)
    parent_platforms = models.JSONField(default=list, null=True, blank=True)

    genres = models.ManyToManyField(Genre, verbose_name="genre", related_name="games")
    stores = models.ManyToManyField(Store, blank=True, verbose_name="stores", related_name="games")
    platforms = models.ManyToManyField(Platform, blank=True, related_name="games")
    tags = models.ManyToManyField(Tag, blank=True, related_name="games")

    def __str__(self):
        return self.name

    @property
    def is_free_to_play(self):
        return self.tags.filter(slug="free-to-play").exists()

    @property
    def min_price_info(self):
        result = self.prices.aggregate(Min('price'))
        return result['price__min']

    @property
    def max_price_info(self):
        result = self.prices.aggregate(Max('retail_price'))
        return result['retail_price__max']

    @property
    def is_upcoming(self):
        return self.released > date.today()

    @property
    def has_icon(self):
        result = []
        for platform in self.parent_platforms or []:
            path = f"catalog/icons/platforms/{platform.lower()}.svg"
            if finders.find(path):
                result.append(platform)
        return result

    def get_absolute_url(self):
        return reverse('game', kwargs={'slug': self.slug})

class Screenshot(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='screenshots')
    image = models.URLField(max_length=500, null=True, blank=True)

    def __str__(self):
        return f"Link for {self.game.name}"

class Rating(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="detail_ratings")
    title = models.CharField(max_length=100, verbose_name="rating")
    count = models.IntegerField(default=0, verbose_name="count")
    percent = models.FloatField(default=0.0, verbose_name="percent")

    def __str__(self):
        return f"{self.title} {self.count} for {self.game.name}"

class Requirement(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="requirements")

    platform_name = models.CharField(max_length=100, verbose_name="Platform name")
    minimum = models.TextField(null=True, blank=True, verbose_name="Minimum")
    recommended = models.TextField(null=True, blank=True, verbose_name="Recommended")

    def __str__(self):
        return f'{self.platform_name} reqs for {self.game.name}'

class GamePrice(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='prices')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='game_prices')
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    retail_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    savings = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    url = models.URLField(max_length=1000, blank=True, null=True)

    class Meta:
        unique_together = ('game', 'store')


class PriceHistory(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='price_history')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='price_history')
    date = models.DateField(auto_now_add=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        ordering = ['-date']

class WishList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_user')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='wishlist_game')
    is_active = models.BooleanField(default=True)
    send_notification = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'game')


class GameRating(models.Model):
    SCORE_CHOICES = [
        ('exceptional', 'Exceptional'),
        ('recommended', 'Recommended'),
        ('meh', 'Meh'),
        ('skip', 'Skip'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='ratings')
    score = models.CharField(max_length=20, choices=SCORE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'game')

@receiver(post_save, sender=Game)
def sync_to_meilisearch(sender, instance, **kwargs):
    document = {
        'id': instance.id,
        'title': instance.name,
        'added': instance.added,
        'rating': float(instance.rating) if instance.rating else 0.0,
        'alternative_names': instance.alternative_names
    }
    client.index('games').add_documents([document])

@receiver(post_delete, sender=Game)
def remove_from_meilisearch(sender, instance, **kwargs):
    client.index('games').delete_document(instance.id)