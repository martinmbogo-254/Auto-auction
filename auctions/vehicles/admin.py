from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import Profile
from django.contrib.auth.models import User
from django.contrib import admin
from django.utils import timezone
from .models import Auction, Vehicle, AuctionHistory
from django.contrib import admin, messages


from .models import (
    VehicleImage, VehicleMake, VehicleModel, 
    ManufactureYear, FuelType, VehicleBody, Vehicle, Bidding, Auction, VehicleView, AuctionHistory
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
class VehicleViewInline(admin.TabularInline):
    model = VehicleView
    extra = 1 

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('registration_no', 'make', 'model', 'YOM', 'mileage', 'engine_cc', 'body_type', 'fuel_type', 'status', 'reserve_price', 'created_at', 'updated_at')
    search_fields = ('make__name', 'registration_no','model__name', 'YOM__year', 'status')
    list_filter = ('status','make', 'model', 'YOM', 'body_type', 'fuel_type', 'created_at', 'updated_at')
    inlines = [VehicleImageInline, BidInline,VehicleViewInline]

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

# vehicles/admin.py

from django.contrib import admin
from django.utils import timezone
from .models import Auction, Vehicle, AuctionHistory
from django.contrib import admin
from django.utils import timezone
from .models import Auction

class EndedFilter(admin.SimpleListFilter):
    title = 'ended'
    parameter_name = 'ended'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Ended'),
            ('No', 'Not Ended'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(end_date__lt=timezone.now())
        if self.value() == 'No':
            return queryset.filter(end_date__gte=timezone.now())

@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    list_display = ('auction_id', 'start_date', 'end_date','created_at', 'approved','is_ended')
    actions = ['update_vehicle_status']
    search_fields = ('vehicles__registration_no','auction_id')
    filter_horizontal = ('vehicles',)
    list_filter = ('approved',EndedFilter,'start_date', 'end_date','created_at')

    
    def is_ended(self, obj):
        return obj.ended
    is_ended.boolean = True
    is_ended.short_description = 'Ended'

    def update_vehicle_status(self, request, queryset):
        now = timezone.now()
        for auction in queryset:
            if auction.end_date <= now and auction.approved:
                for vehicle in auction.vehicles.all():
                    highest_bid = vehicle.bidding.order_by('-amount').first()
                    if highest_bid and highest_bid.amount >= vehicle.reserve_price:
                        vehicle.status = 'sold'
                        AuctionHistory.objects.filter(vehicle=vehicle, auction=auction).update(sold=True, returned_to_available=False)
                    else:
                        vehicle.status = 'available'
                        AuctionHistory.objects.filter(vehicle=vehicle, auction=auction).update(sold=False, returned_to_available=True)
                    vehicle.save()
                self.message_user(request, f"Updated vehicle statuses for auction {auction.auction_id}" , level=messages.SUCCESS)
            else:
                self.message_user(request, f"Auction {auction.auction_id} is not yet ended or not approved ", level=messages.ERROR)
    update_vehicle_status.short_description = "Update Vehicle Statuses for Selected Auctions"

# @admin.register(Auction)
# class AuctionAdmin(admin.ModelAdmin):
#     list_display = ('auction_id',)
#     search_fields = ('auction_id',)
# @admin.register(CustomUser)
# class CustomUserAdmin(admin.ModelAdmin):
#     # list_display = ('email', 'phone_number', 'id_number', 'name', 'is_admin', 'created_at')
#     # search_fields = ('email', 'phone_number', 'id_number', 'name')
#     # list_filter = ('is_admin', 'created_at')

@admin.register(AuctionHistory)
class AuctionHistoryAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'auction', 'start_date', 'end_date', 'sold', 'returned_to_available')
    search_fields = ('vehicle__registration_no', 'auction__auction_id')

    def vehicle_registration_no(self, obj):
        return obj.vehicle.registration_no
    vehicle_registration_no.short_description = 'Vehicle Registration No'
    
    def auction_id(self, obj):
        return obj.auction.auction_id
    auction_id.short_description = 'Auction ID'

admin.site.site_header = "RSVA Admin"
admin.site.site_title = "RSVA"
admin.site.index_title = "Welcome to RSVA Admin"