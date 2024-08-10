from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Auction

@receiver(post_save, sender=Auction)
def update_auction_status(sender, instance, **kwargs):
    instance.check_and_update_status()
