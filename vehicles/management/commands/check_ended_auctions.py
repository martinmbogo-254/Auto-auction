# auctions/management/commands/check_ended_auctions.py
from django.core.management.base import BaseCommand
from vehicles.models import Auction

class Command(BaseCommand):
    help = 'Check and process ended auctions'

    def handle(self, *args, **options):
        processed_count = Auction.process_ended_auctions()
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed {processed_count} ended auctions'
            )
        )