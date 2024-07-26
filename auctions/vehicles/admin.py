from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import Profile
from django.contrib.auth.models import User

from .models import (
    VehicleImage, VehicleMake, VehicleModel, 
    ManufactureYear, FuelType, VehicleBody, Vehicle, Bidding, Auction, VehicleView
)
# class ProfileInline(admin.StackedInline):
#     model = Profile
#     can_delete = False
#     verbose_name_plural = 'Profiles'

# class MyUser (UserAdmin):
#     inlines = (ProfileInline,)

# admin.site.unregister(User)
# admin.site.register(User,MyUser)

class VehicleImageInline(admin.TabularInline):
    model = VehicleImage
    extra = 1  # Number of empty forms to display

class BidInline(admin.TabularInline):
    model = Bidding
    extra = 1  # Number of empty forms to display

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('id', 'make', 'model', 'YOM', 'mileage', 'engine_cc', 'body_type', 'fuel_type', 'get_bid_status_display', 'reserve_price', 'created_at', 'updated_at')
    search_fields = ('make__name', 'model__name', 'YOM__year', 'created_by__email', 'bid_status')
    list_filter = ('make', 'model', 'YOM', 'body_type', 'fuel_type', 'created_at', 'updated_at')
    inlines = [VehicleImageInline, BidInline]

@admin.register(VehicleView)
class VehicleViewAdmin(admin.ModelAdmin):
    list_display = ( 'id',)
    search_fields = ('id',)

@admin.register(VehicleMake)
class VehicleMakeAdmin(admin.ModelAdmin):
    list_display = ( 'name',)
    search_fields = ('name',)

@admin.register(VehicleModel)
class VehicleModelAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(ManufactureYear)
class ManufactureYearAdmin(admin.ModelAdmin):
    list_display = ('year',)
    search_fields = ('year',)

@admin.register(FuelType)
class FuelTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    class Meta:
        verbose_name_plural = "Fuel Types"

@admin.register(VehicleBody)
class VehicleBodyAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    list_display = ('auction_id',)
    search_fields = ('auction_id',)
# @admin.register(CustomUser)
# class CustomUserAdmin(admin.ModelAdmin):
#     # list_display = ('email', 'phone_number', 'id_number', 'name', 'is_admin', 'created_at')
#     # search_fields = ('email', 'phone_number', 'id_number', 'name')
#     # list_filter = ('is_admin', 'created_at')



admin.site.site_header = "RSVA Admin"
admin.site.site_title = "RSVA"
admin.site.index_title = "Welcome to RSVA Admin"