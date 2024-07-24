from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE
    )
    id_number = models.IntegerField(max_length=10,blank=False,null=True,unique=True)
    phone_number = models.IntegerField(max_length=10,blank=False,null=True,unique=True)

    

    def __str__(self):
        return f"{self.user.username}'s profile"