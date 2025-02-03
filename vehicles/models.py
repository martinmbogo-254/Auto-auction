from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from ckeditor.fields import RichTextField
from django.utils.html import format_html
from django.http import HttpResponseForbidden
from django.contrib.auth.models import Group
from django.utils import timezone
from datetime import timedelta
from django.utils.text import slugify



class VehicleMake(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "Makes"
    def __str__(self):
            return self.name

class VehicleModel(models.Model):
    make = models.ForeignKey(VehicleMake, related_name='models', on_delete=models.CASCADE,blank=True,null=True)
    name = models.CharField(max_length=255)
    class Meta:
        verbose_name_plural = "Models"
    def __str__(self):
            return self.name

class ManufactureYear(models.Model):
    year = models.IntegerField()
    class Meta:
        verbose_name_plural = "Years of Manufacture"
    def __str__(self):
            return str(self.year)   

class FuelType(models.Model):
    name = models.CharField(max_length=255)
    class Meta:
        verbose_name_plural = "Fuel Types"
    def __str__(self):
            return self.name

class VehicleBody(models.Model):
    name = models.CharField(max_length=255)
    class Meta:
        verbose_name_plural = " Vehicle Bodies"
    def __str__(self):
            return self.name
class Yard(models.Model):
    name = models.CharField(max_length=255)
    link = models.CharField(max_length=255)

    def __str__(self):
            return self.name
class Financier(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self):
            return self.name
class Vehicle(models.Model):
    BID_STATUS_CHOICES = [
        ('idle', 'idle'),
        ('available', 'available'),
        ('on_auction', 'on_auction'),
        ('on_bid', 'on_bid'),
        ('bid_won','bid_won'),
        ('sold', 'sold'),
    ]
    TRANSMISSION_CHOICES=[
        ('Automatic','Automatic'),
        ('Manual','Manual'),
    ]
    v_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    Financier = models.ForeignKey(Financier, null=True, blank=True, on_delete=models.SET_DEFAULT,default='MyCredit Ltd')
    registration_no = models.CharField(max_length=255,unique=True)
    make = models.ForeignKey(VehicleMake, on_delete=models.SET_DEFAULT,default='Vehicle')
    model = models.ForeignKey(VehicleModel, on_delete=models.SET_DEFAULT, default='SUV')
    YOM = models.ForeignKey(ManufactureYear, on_delete=models.SET_DEFAULT, default='2010')
    mileage = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    engine_cc = models.IntegerField()
    transmission = models.CharField(max_length=255, choices=TRANSMISSION_CHOICES,blank=True)
    body_type = models.ForeignKey(VehicleBody, on_delete=models.CASCADE)
    fuel_type = models.ForeignKey(FuelType, on_delete=models.CASCADE)
    color = models.CharField(max_length=10,default ='white')
    seats = models.IntegerField(default=5)
    yard = models.ForeignKey(Yard, on_delete=models.CASCADE, blank=True, null=True)
    status = models.CharField(max_length=10, choices=BID_STATUS_CHOICES, default='idle')
    reserve_price = models.IntegerField()
    description = RichTextField(blank=True)
    file = models.FileField(upload_to='images/',default='images/default-vehicle.png',blank=True)
    views = models.IntegerField(default=0)
    is_hotsale = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, related_name="approved_vehicles", null=True, blank=True, on_delete=models.SET_NULL)
    approved_at = models.DateTimeField(null=True, blank=True)
    # is_disapproved = models.BooleanField(default=False)
    disapproved_by = models.ForeignKey(User, related_name="disapproved_vehicles", null=True, blank=True, on_delete=models.SET_NULL)
    disapproved_at = models.DateTimeField(null=True, blank=True)
    
    # Method to generate a URL-friendly slug for the registration number
    def slugified_registration_no(self):
        return slugify(self.registration_no)

    def approve(self, user):
        """Approve the vehicle and set approved fields."""
        self.is_approved = True
        # self.is_disapproved = False
        self.approved_by = user
        self.approved_at = timezone.now()
        self.status = 'available'  # Automatically set to available if approved
        self.save()

    def disapprove(self, user):
        """Disapprove the vehicle and set approved fields."""
        # self.disapproved = True
        self.is_approved = False
        self.disapproved_by = user
        self.disapproved_at = timezone.now()
        self.status = 'idle'  # Automatically set to available if approved
        self.save()
        
    def get_absolute_url(self):
        return reverse('detail', kwargs={'registration_no': self.registration_no})
    def __str__(self):
            return self.registration_no

    def is_available(self):
        return self.status == 'available'
        
    def is_sold(self):
            return self.status == 'sold'

    def days_since_creation(self):
        now = timezone.now()
        delta = now - self.created_at
        return delta.days

    def current_auction_end_date(self):
        current_auction = self.auctions.filter(end_date__gte=timezone.now()).order_by('end_date').first()
        if current_auction:
            return current_auction.end_date
        return None
    
    

class VehicleImage(models.Model):
    vehicle= models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    image = models.FileField(upload_to='vehicleimages/',default='images/default-vehicle.png')
    class Meta:
        verbose_name_plural = "Images"

class Bidding(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='bidding')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.IntegerField()
    is_auction_bid = models.BooleanField(default=False) 
    awarded = models.BooleanField(default=False)  # To track awarded status
    discarded = models.BooleanField(default=False)
    bid_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f" Bid for {self.vehicle.registration_no} by {self.user.username} at Ksh {self.amount}"

    def save(self, *args, **kwargs):
        # Check if this is a new bid (no ID yet)
        if not self.pk:
            # Get the related auction for the vehicle
            active_auction = self.vehicle.auctions.filter(
                start_date__lte=timezone.now(),
                end_date__gte=timezone.now()
            ).first()
            
            # If there's an active auction, mark as auction bid
            if active_auction:
                self.is_auction_bid = True
                
                # Handle auction extension logic
                if not active_auction.has_extended:
                    time_left = active_auction.end_date - timezone.now()
                    if time_left <= timedelta(minutes=5):
                        # Add 5 minutes to the auction end time
                        active_auction.end_date = active_auction.end_date + timedelta(minutes=5)
                        active_auction.has_extended = True
                        active_auction.save()
            
            # If no active auction and is_auction_bid not already True, set to False
            # This ensures we don't override any existing True value
            elif not self.is_auction_bid:
                self.is_auction_bid = False

    # def save(self, *args, **kwargs):
    #     # Get the related auction for the vehicle
    #     vehicle = self.vehicle
    #     auction = vehicle.auctions.filter(end_date__gte=timezone.now()).first()

    #     # Check if the auction exists and if the bid is placed within the last 5 minutes
    #     if auction and not auction.has_extended:
    #         time_left = auction.end_date - timezone.now()
    #         if time_left <= timedelta(minutes=5):
    #             # Add 5 minutes to the auction end time if the bid is placed within the last 5 minutes
    #             auction.end_date = auction.end_date + timedelta(minutes=5)
    #             auction.has_extended = True  # Mark that the auction has been extended
    #             auction.save()  # Save the updated auction with the new end time
        
        super(Bidding, self).save(*args, **kwargs)  # Call the original save method

class AwardHistory(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.IntegerField()
    awarded_at = models.DateTimeField(auto_now_add=True)
    awarded_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='awarder')

    def __str__(self):
        return f"Awarded {self.vehicle.registration_no} to {self.user.username} at Ksh {self.amount}"

class Auction(models.Model):
    auction_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    # current_time = models.DateTimeField(default=timezone.now())
    created_at = models.DateTimeField(auto_now_add=True)
    vehicles = models.ManyToManyField('Vehicle', related_name='auctions')
    approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, related_name="approved_auctions", null=True, blank=True, on_delete=models.SET_NULL)
    approved_at = models.DateTimeField(null=True, blank=True)
    processed = models.BooleanField(default=False)
    has_extended = models.BooleanField(default=False)  # Flag to track if the end time was extended
    
    

    def __str__(self):
        return f"Auction {self.auction_id}"

    def get_auction_status(self):
            active_auctions = self.auctions.filter(end_date < timezone.now(), approved=True)
            if active_auctions.exists():
                return 'Active'
            return 'Ended'

        # Custom admin action to approve auctions
    

    def check_and_update_status(self):
        if self.end_date < timezone.now():
            for vehicle in self.vehicles.all():
                highest_bid = vehicle.bidding.order_by('-amount').first()
                if highest_bid and highest_bid.amount >= vehicle.reserve_price:
                    vehicle.status = 'sold'
                    AuctionHistory.objects.filter(vehicle=vehicle, auction=self).update(sold=True)
                else:
                    vehicle.status = 'available'
                vehicle.save()
    @property
    def ended(self):
        return self.end_date < timezone.now()

    def process_if_ended(self):
        """Check and process the auction if it has ended"""
        now = timezone.now()
        if self.end_date <= now and self.approved and not self.processed:
            from .signals import process_ended_auction
            process_ended_auction(self)
            return True
        return False

    @classmethod
    def process_ended_auctions(cls):
        """Process all ended auctions"""
        now = timezone.now()
        ended_auctions = cls.objects.filter(
            end_date__lte=now,
            approved=True,
            processed=False
        )
        processed_count = 0
        for auction in ended_auctions:
            if auction.process_if_ended():
                processed_count += 1
        return processed_count
class VehicleView(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('vehicle', 'user')

    def __str__(self):
            return self.vehicle.make.name


class AuctionHistory(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.RESTRICT, related_name='auction_history')
    auction = models.ForeignKey(Auction, on_delete=models.RESTRICT, related_name='auction_history')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    on_bid = models.BooleanField(default=False,)
    returned_to_available = models.BooleanField(default=False)
    sold = models.BooleanField(default=False)
    class Meta:
        verbose_name_plural = " Auction Histories"

    def __str__(self):
        return f"{self.vehicle.registration_no} {self.vehicle.model.name} in Auction {str(self.auction.auction_id)[:8]}"

     # Method to get the top bid amount
    def top_bid_amount(self):
        top_bid = self.vehicle.bidding.order_by('-amount').first()  # Get the highest bid
        return top_bid.amount if top_bid else "No bids"

    # Method to show the reserve price of the vehicle
    def reserve_price(self):
        return self.vehicle.reserve_price

     # Method to get the highest bidder's email
    def highest_bidder_email(self):
        top_bid = self.vehicle.bidding.order_by('-amount').first()  # Get the highest bid
        return top_bid.user.email if top_bid else "No bids"

    # Method to count the total number of bids
    def total_bids(self):
        return self.vehicle.bidding.count()

# Example Recipient model
class NotificationRecipient(models.Model):
    email = models.EmailField()
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.email
