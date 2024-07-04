from django.db import models



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

class User(models.Model):
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    id_number = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255)
    is_admin = models.BooleanField(default=False)

class Vehicle(models.Model):
    BID_STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('pending', 'Pending'),
        ('won', 'Won'),
        ('lost', 'Lost'),
    ]
    make = models.ForeignKey(VehicleMake, on_delete=models.CASCADE)
    model = models.ForeignKey(VehicleModel, on_delete=models.CASCADE)
    YOM = models.ForeignKey(ManufactureYear, on_delete=models.CASCADE)
    mileage = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    engine_cc = models.IntegerField()
    body_type = models.ForeignKey(VehicleBody, on_delete=models.CASCADE)
    fuel_type = models.ForeignKey(FuelType, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    bid_status = models.CharField(max_length=10, choices=BID_STATUS_CHOICES, default='open')
    reserve_price = models.IntegerField()

class VehicleImage(models.Model):
    vehicle= models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    image = models.CharField(max_length=255)
    class Meta:
        verbose_name_plural = "Images"

class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    amount = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
