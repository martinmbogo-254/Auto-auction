from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Profile, Location

admin.site.register(Profile)
admin.site.register (Location)

