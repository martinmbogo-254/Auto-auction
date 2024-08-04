from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import Profile
from django.contrib.auth.models import User
from django.contrib import admin
from django.utils import timezone
from .models import Auction, Vehicle, AuctionHistory
from django.contrib import admin, messages
from .forms import AuctionForm
from django.utils import timezone
from .models import (
    VehicleImage, VehicleMake, VehicleModel, 
    ManufactureYear, FuelType, VehicleBody, Vehicle, Bidding, Auction, VehicleView, AuctionHistory
)


class VehicleImageInline(admin.TabularInline):
    model = VehicleImage
    extra = 1  # Number of empty forms to display

class BidInline(admin.TabularInline):
    model = Bidding
    readonly_fields = ('user', 'amount', 'created_at',)  
    # extra = 1  
    can_delete = False

class VehicleViewInline(admin.TabularInline):
    model = VehicleView
    extra = 1 
    readonly_fields=('vehicle','user','viewed_at')
    can_delete = False


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('registration_no', 'make', 'model', 'YOM', 'mileage', 'engine_cc', 'body_type', 'fuel_type', 'status', 'reserve_price', 'created_at', 'updated_at','days_since_creation','current_auction_end_date')
    search_fields = ('make__name', 'registration_no','model__name', 'YOM__year', 'status')
    list_filter = ('status','make', 'model', 'YOM', 'body_type', 'fuel_type', 'created_at', 'updated_at')
    inlines = [VehicleImageInline, BidInline,VehicleViewInline]

    def current_auction_end_date(self, obj):
        return obj.current_auction_end_date()
    current_auction_end_date.short_description = 'Auction End Date'

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

class AuctionHistoryInline(admin.TabularInline):
    model = AuctionHistory
    extra = 0
    readonly_fields = ('vehicle', 'start_date', 'end_date', 'on_bid', 'returned_to_available')
    can_delete = False

@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    list_display = ('id','auction_id', 'start_date', 'end_date','created_at', 'approved','is_ended')
    actions = ['update_vehicle_status']
    search_fields = ('vehicles__registration_no','auction_id')
    filter_horizontal = ('vehicles',)
    list_filter = ('approved',EndedFilter,'start_date', 'end_date','created_at')
    inlines = [AuctionHistoryInline]

    def get_form(self, request, obj=None, **kwargs):
        # Call the superclass method to get the form class
        form = super().get_form(request, obj, **kwargs)
        # Modify the form's vehicle queryset
        form.base_fields['vehicles'].queryset = Vehicle.objects.filter(status='available')
        return form
    
    def is_ended(self, obj):
        return obj.ended
    is_ended.boolean = True
    is_ended.short_description = 'Ended'
   

    def save_model(self, request, obj, form, change):
            super().save_model(request, obj, form, change)
            selected_vehicles = form.cleaned_data['vehicles']
            for vehicle in selected_vehicles:
                vehicle.status = 'on_auction'  # Update this status based on your needs
                vehicle.save()
                AuctionHistory.objects.create(
                    vehicle=vehicle,
                    auction=obj,
                    start_date=obj.start_date,
                    end_date=obj.end_date,
                    on_bid=False
                )


    def update_vehicle_status(self, request, queryset):
        now = timezone.now()
        for auction in queryset:
            if auction.end_date <= now and auction.approved:
                for vehicle in auction.vehicles.all():
                    highest_bid = vehicle.bidding.order_by('-amount').first()
                    if highest_bid and highest_bid.amount >= vehicle.reserve_price:
                        vehicle.status = 'on_bid'
                        AuctionHistory.objects.filter(vehicle=vehicle, auction=auction).update(on_bid=True, returned_to_available=False)
                    else:
                        vehicle.status = 'available'
                        AuctionHistory.objects.filter(vehicle=vehicle, auction=auction).update(on_bid=False, returned_to_available=True)
                    vehicle.save()
                self.message_user(request, f"Updated vehicle statuses for auction {auction.auction_id}" , level=messages.SUCCESS)
            else:
                self.message_user(request, f"Auction {auction.auction_id} is not yet ended or not approved ", level=messages.ERROR)
    update_vehicle_status.short_description = "Update Vehicle Statuses for Selected Auctions"

    def changelist_view(self, request, extra_context=None):
        # Check if there is an active auction
        now = timezone.now()
        has_active_auction = Auction.objects.filter(end_date__gt=now, approved=True).exists()
        extra_context = extra_context or {}
        extra_context['has_active_auction'] = has_active_auction

        return super().changelist_view(request, extra_context=extra_context)

class VehicleInline(admin.TabularInline):
    model = AuctionHistory
    extra = 0
    readonly_fields = ['vehicle', 'start_date', 'end_date', 'on_bid', 'returned_to_available']
    # fields = ['vehicle', 'start_date', 'end_date', 'on_bid', 'returned_to_available']


@admin.register(AuctionHistory)
class AuctionHistoryAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'auction', 'start_date', 'end_date', 'on_bid', 'returned_to_available')
    search_fields = ('vehicle__registration_no', 'auction__auction_id')
    readonly_fields = ('vehicle', 'auction', 'start_date', 'end_date', 'on_bid', 'returned_to_available')
    # inlines = [BidInline]


    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('vehicle', 'auction').prefetch_related('vehicle__bidding')
        return queryset

    def vehicle_details(self, obj):
        highest_bid = obj.vehicle.bidding.order_by('-amount').first()
        return highest_bid.amount if highest_bid else 'No Bids'
    
    vehicle_details.short_description = 'Highest Bid'

    def vehicle_registration_no(self, obj):
        return obj.vehicle.registration_no
    vehicle_registration_no.short_description = 'Vehicle Registration No'
    
    def auction_id(self, obj):
        return obj.auction.auction_id[:8]
    auction_id.short_description = 'Auction ID'

admin.site.site_header = "RSVA Admin"
admin.site.site_title = "RSVA"
admin.site.index_title = "Welcome to RSVA Admin"