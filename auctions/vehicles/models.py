from django.db import models

class Vehicle(models.Model):
    make = models.ForeignKey(VehicleMake, on_delete=models.CASCADE)