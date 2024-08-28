from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
from django.db import models
from django.contrib.auth.models import User


# # Create your models here.
# class CustomUser(AbstractUser):
#     username = models.CharField(max_length=150, unique=False, blank=True, null=True)
#     email = models.EmailField(unique=True)

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['username']
class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE
    )
    id_number = models.IntegerField(max_length=10,blank=False,null=True,unique=True)
    phone_number = models.IntegerField(max_length=10,blank=False,null=True,unique=True)

    

    def __str__(self):
        return f"{self.user.username}'s profile"