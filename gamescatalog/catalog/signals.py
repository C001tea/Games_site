from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Store

@receiver([post_save, post_delete], sender=Store)
def clear_store_cache(sender, **kwargs):
        cache.delete("all_stores")