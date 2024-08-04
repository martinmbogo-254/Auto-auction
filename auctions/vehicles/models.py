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

class Vehicle(models.Model):
    BID_STATUS_CHOICES = [
        ('available', 'available'),
        ('on_auction', 'on_auction'),
        ('on_bid', 'on_bid'),
    ]
    v_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    registration_no = models.CharField(max_length=255,unique=True)
    make = models.ForeignKey(VehicleMake, on_delete=models.CASCADE)
    model = models.ForeignKey(VehicleModel, on_delete=models.CASCADE)
    YOM = models.ForeignKey(ManufactureYear, on_delete=models.CASCADE)
    mileage = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    engine_cc = models.IntegerField()
    body_type = models.ForeignKey(VehicleBody, on_delete=models.CASCADE)
    fuel_type = models.ForeignKey(FuelType, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=BID_STATUS_CHOICES, default='available')
    reserve_price = models.IntegerField()
    file = models.FileField(upload_to='images/',default='images/default-vehicle.png',blank=True)
    views = models.IntegerField(default=0)

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
    image = models.FileField(upload_to='vehicleimages/',default='images/default-vehicle.png',blank=True)
    class Meta:
        verbose_name_plural = "Images"

class Bidding(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='bidding')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

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
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='auction_history')
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='auction_history')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    on_bid = models.BooleanField(default=False,)
    returned_to_available = models.BooleanField(default=False)
    class Meta:
        verbose_name_plural = " Auction Histories"

    def __str__(self):
        return f"{self.vehicle.registration_no} {self.vehicle.model.name} in Auction {str(self.auction.auction_id)[:8]}"