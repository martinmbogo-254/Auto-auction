# auctions/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import strip_tags
from .models import Auction

@receiver(post_save, sender=Auction)
def check_auction_end(sender, instance, created, **kwargs):
    now = timezone.now()
    if not created and instance.approved and not instance.processed and instance.end_date <= now:
        process_ended_auction(instance)

def process_ended_auction(auction):
    """Process an ended auction - update vehicle statuses and send winner emails"""
    try:
        for vehicle in auction.vehicles.all():
            # Get the highest bid for the vehicle
            highest_bid = vehicle.bidding.order_by('-amount').first()
            
            if highest_bid and highest_bid.amount >= vehicle.reserve_price:
                vehicle.status = 'bid_won'
                send_winner_email(highest_bid)
            else:
                vehicle.status = 'available'
            vehicle.save()
        
        # Mark auction as processed
        auction.processed = True
        auction.save()
    except Exception as e:
        print(f"Error processing auction {auction.auction_id}: {str(e)}")

def send_winner_email(winning_bid):
    """Send email notification to auction winner"""
    context = {
        'username': winning_bid.user.username,
        'registration_no': winning_bid.vehicle.registration_no,
        'amount': "{:,.2f}".format(winning_bid.amount),
        'email': winning_bid.user.email
    }
    
    html_message = render_to_string('vehicles/emails/bidwin.html', context)
    plain_message = strip_tags(html_message)
    subject = f"Congratulations! You've won the bid for {winning_bid.vehicle.registration_no}"

    send_mail(
        subject=subject,
        message=plain_message,
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[winning_bid.user.email],
        fail_silently=False
    )