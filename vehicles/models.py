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


class VehicleMake(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "Makes"
    def __str__(self):
            return self.name

class VehicleModel(models.Model):
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
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='images/',default='images/default-vehicle.png',blank=True)
    views = models.IntegerField(default=0)

    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, related_name="approved_vehicles", null=True, blank=True, on_delete=models.SET_NULL)
    approved_at = models.DateTimeField(null=True, blank=True)

    def approve(self, user):
        """Approve the vehicle and set approved fields."""
        self.is_approved = True
        self.approved_by = user
        self.approved_at = timezone.now()
        self.status = 'available'  # Automatically set to available if approved
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
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f" Bid for {self.vehicle.registration_no} by {self.user.username} at Ksh {self.amount}"

class Auction(models.Model):
    auction_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    # current_time = models.DateTimeField(default=timezone.now())
    created_at = models.DateTimeField(auto_now_add=True)
    vehicles = models.ManyToManyField('Vehicle', related_name='auctions')
    approved = models.BooleanField(default=False)
    def __str__(self):
        return f"Auction {self.auction_id}"
    def get_auction_status(self):
            active_auctions = self.auctions.filter(end_date < timezone.now(), approved=True)
            if active_auctions.exists():
                return 'Active'
            return 'Ended'

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
