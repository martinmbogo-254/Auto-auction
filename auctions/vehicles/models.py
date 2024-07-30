from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import User
import uuid


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
        ('sold', 'sold'),
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
    status = models.CharField(max_length=10, choices=BID_STATUS_CHOICES, default='open')
    reserve_price = models.IntegerField()
    file = models.FileField(upload_to='images/',default='images/default-vehicle.png',blank=True)
    views = models.IntegerField(default=0)

    def __str__(self):
            return self.registration_no

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
    vehicles = models.ManyToManyField('Vehicle', related_name='auctions')
    approved = models.BooleanField(default=False)
    def __str__(self):
        return f"Auction {self.auction_id} from {self.start_date} to {self.end_date}"

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
    sold = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = " Auction Histories"

    def __str__(self):
        return f"{self.vehicle.make.name} {self.vehicle.model.name} in Auction {str(self.auction.auction_id)[:8]}"