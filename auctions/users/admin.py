from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Profile

admin.site.register(Profile)
class VehicleMakeAdmin(admin.ModelAdmin):
    list_display = ( 'id_number',)
    search_fields = ('id_number',)
