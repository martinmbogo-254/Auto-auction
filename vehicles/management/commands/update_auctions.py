from django.core.management.base import BaseCommand
from django.utils import timezone
from auction.models import Auction

class Command(BaseCommand):
    help = 'Update auction statuses and vehicle statuses'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        auctions = Auction.objects.filter(end_date__lte=now, approved=True)
        for auction in auctions:
            auction.save()  # This will trigger the post_save signal and update statuses
        self.stdout.write(self.style.SUCCESS('Successfully updated auction statuses'))
