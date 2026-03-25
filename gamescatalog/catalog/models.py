from django.db import models

class Store(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name="Name")
    domain = models.CharField(max_length=150, verbose_name="domain")

    def __str__(self):
        return self.name


class Games(models.Model):
    id = models.IntegerField(primary_key=True)
    slug = models.SlugField(max_length=255, unique=True)
    name = models.CharField(max_length=255, verbose_name="Name")
    released = models.DateField(null=True, blank=True, verbose_name="released")
    rating = models.FloatField(default=0.0, verbose_name="rating")
    rating_count = models.IntegerField(default=0, verbose_name="Ratings count")
    image = models.URLField(max_length=500, null=True, blank=True, verbose_name="image")
    description = models.TextField(null=True, blank=True, verbose_name="Description")

    stores = models.ManyToManyField(Store, blank=True, verbose_name="stores")

    def __str__(self):
        return self.name

class Screenshots(models.Model):
    game = models.ForeignKey(Games, on_delete=models.CASCADE, related_name='screenshots')
    image = models.URLField(max_length=500, null=True, blank=True)

    def __str__(self):
        return f"Link for {self.game.name}"

class Ratings(models.Model):
    game = models.ForeignKey(Games, on_delete=models.CASCADE, related_name="detail_ratings")
    title = models.CharField(max_length=100, verbose_name="rating")
    count = models.IntegerField(default=0, verbose_name="count")
    percent = models.FloatField(default=0.0, verbose_name="percent")

    def __str__(self):
        return f"{self.title} {self.count} for {self.game.name}"

class Requirements(models.Model):
    game = models.ForeignKey(Games, on_delete=models.CASCADE, related_name="requirements")

    platform_name = models.CharField(max_length=100, verbose_name="Platform name")
    minimum = models.TextField(null=True, blank=True, verbose_name="Minimum")
    recommended = models.TextField(null=True, blank=True, verbose_name="Recommended")

    def __str__(self):
        return f'{self.platform_name} reqs for {self.game.name}'