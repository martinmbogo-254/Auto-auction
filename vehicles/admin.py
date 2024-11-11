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
from django.contrib import admin
from django.utils import timezone
from .models import Auction, Vehicle, AuctionHistory
from django.contrib import admin
from django.utils import timezone
from .models import Auction
from .models import (
    VehicleImage, VehicleMake, VehicleModel, 
    ManufactureYear, FuelType, VehicleBody, Vehicle, Bidding, Auction, VehicleView, AuctionHistory,NotificationRecipient,Financier,Yard
)


from django.contrib import admin
from django.http import HttpResponse
import csv
from django.core.mail import send_mail
from django.conf import settings


# Add a description to the custom action


@admin.register(Bidding)
class BidAdmin(admin.ModelAdmin):
    search_fields = ('vehicle__registration_no','user__username')
    list_display = ('vehicle', 'user', 'amount', 'created_at')
    actions = ['generate_bid_report']

    def generate_bid_report(self, request, queryset):
        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="bid_report.csv"'
        writer = csv.writer(response)
        writer.writerow(['vehicle', 'user', 'amount', 'created_at'])

        for bid in queryset:
            writer.writerow([
                bid.vehicle.registration_no,
                bid.user.username, 
                bid.amount,
                bid.created_at])
        
        return response
    generate_bid_report.short_description = "Generate bid report for selected vehicles"

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
    # extra = 1 
    readonly_fields=('vehicle','user','viewed_at')
    can_delete = False


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('registration_no','Financier','make', 'model', 'YOM', 'mileage', 'engine_cc', 'body_type','color','yard', 'fuel_type','is_approved', 'status', 'reserve_price', 'created_at', 'updated_at','days_since_creation','current_auction_end_date')
    search_fields = ('make__name', 'registration_no','model__name', 'YOM__year', 'status')
    list_filter = ('status','make', 'model', 'YOM', 'body_type', 'fuel_type', 'created_at', 'updated_at','is_approved')
    inlines = [VehicleImageInline, BidInline,VehicleViewInline]
    readonly_fields = ('views','status','approved_by', 'approved_at','is_approved')
    actions = ['make_available', 'generate_vehicle_report','sell','approve_vehicle']
    
    # Custom action for generating reports
    def generate_vehicle_report(self, request, queryset):
        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="vehicle_report.csv"'

        writer = csv.writer(response)
        writer.writerow(['Registration No','Financier', 'Make', 'Model', 'Year of Manufacture', 'Mileage','Transmission',  'Engine CC','Body Type', 'Seats','Color','Fuel Type','Storage Yard', 'Reserve Price', 'Status', 'Days Since Creation'])

        # Iterate over the selected vehicles in the admin panel
        for vehicle in queryset:
            writer.writerow([
                vehicle.registration_no,
                vehicle.Financier,
                vehicle.make.name,
                vehicle.model.name,
                vehicle.YOM.year,
                vehicle.mileage,
                vehicle.transmission,
                vehicle.engine_cc,
                vehicle.body_type.name,
                vehicle.seats,
                vehicle.color,
                vehicle.fuel_type.name,
                vehicle.yard,
                vehicle.reserve_price,
                vehicle.status,
                vehicle.days_since_creation(),
            ])

        return response
    generate_vehicle_report.short_description = "Generate CSV report for selected vehicles"
    def make_available(self, request, queryset):
        updated = queryset.update(status='available')
        self.message_user(request, f"{updated} vehicle(s) successfully marked as available.")
    
    make_available.short_description = "Mark selected vehicles as available"

    def sell(self, request, queryset):
        updated = queryset.update(status='sold')
        self.message_user(request, f"{updated} vehicle(s) successfully sold")
    
    sell.short_description = "Mark selected vehicles as sold"
    def current_auction_end_date(self, obj):
        return obj.current_auction_end_date()
    current_auction_end_date.short_description = 'Auction End Date'

    # def get_queryset(self, request):
    #     """Limit what different users see based on role."""
    #     qs = super().get_queryset(request)
    #     if request.user.groups.filter(name='Sales').exists():
    #         return qs.filter(is_approved=True)  # Makers see only unapproved vehicles
    #     return qs  # Checkers and other users see all vehicles

    def get_readonly_fields(self, request, obj=None):
        """Make fields read-only for Admins to prevent modification."""
        if request.user.groups.filter(name='Admins').exists():
            return self.readonly_fields + tuple(field.name for field in self.model._meta.fields if field.name != 'is_approved')
        return self.readonly_fields

    # Admin action for Checkers to approve vehicles
    def approve_vehicle(self, request, queryset):
        if not request.user.groups.filter(name='Admins').exists():
            self.message_user(request, "Only Admins can approve vehicles.", level=messages.WARNING)
            return

        # Update selected vehicles
        count = 0
        for vehicle in queryset.filter(is_approved=False):
            vehicle.approve(request.user)
            count += 1

        self.message_user(request, f"{count} vehicle(s) have been approved.", level=messages.SUCCESS)

    approve_vehicle.short_description = "Approve selected vehicles"

admin.site.register(NotificationRecipient)
admin.site.register(Financier)
admin.site.register(Yard)
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
    readonly_fields = ('vehicle', 'start_date', 'end_date', 'on_bid', 'returned_to_available','sold')
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
                    # Get the highest bid for the vehicle
                    highest_bid = vehicle.bidding.order_by('-amount').first()
                    if highest_bid and highest_bid.amount >= vehicle.reserve_price:
                        vehicle.status = 'sold'
                        # Send an email to the winner
                        self.send_winner_email(highest_bid)
                    else:
                        vehicle.status = 'available'
                    vehicle.save()
                
                self.message_user(request, f"Updated vehicle statuses for auction {auction.auction_id}", level=messages.SUCCESS)
            else:
                self.message_user(request, f"Auction {auction.auction_id} is not yet ended or not approved.", level=messages.ERROR)
    update_vehicle_status.short_description = "Update Vehicle Statuses for Selected Auctions"

    # Method to send email notification to the winner
    def send_winner_email(self, winning_bid):
        subject = f"Congratulations! You've won the bid for {winning_bid.vehicle.registration_no}"
        message = (
            f"Dear {winning_bid.user.username},\n\n"
            f"Congratulations! You have won the auction for the vehicle {winning_bid.vehicle.registration_no}.\n"
            f"Your winning bid amount: Ksh {winning_bid.amount}.\n\n"
            "We will contact you shortly with the next steps.\n\n"
            "Thank you for participating in our auction.\n\n"
            "Best regards,\n"
            "Riverlong Auction Team"
        )
        recipient_list = [winning_bid.user.email]
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=False)
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
    list_display = [
        'vehicle', 'auction', 'start_date', 'end_date', 'reserve_price', 'total_bids',
        'top_bid_amount', 'highest_bidder_email',  
         'on_bid', 'returned_to_available','sold'
    ]
    list_filter = (
        'vehicle', 'start_date', 'end_date',
         'on_bid', 'returned_to_available','sold'
    )
    search_fields = ('vehicle__registration_no', 'auction__auction_id')
    readonly_fields = ('vehicle', 'auction', 'start_date', 'end_date', 'on_bid', 'returned_to_available')
    # inlines = [BidInline]
    actions =['history_report','vehicle_details']

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


    def highest_bidder_email(self, obj):
        return obj.highest_bidder_email()

    def total_bids(self, obj):
        return obj.total_bids()

    def top_bid_amount(self, obj):
        return obj.top_bid_amount()

    def reserve_price(self, obj):
        return obj.reserve_price()

   # Action to export selected AuctionHistory records as CSV
    def history_report(self, request, queryset):
        # Define the HTTP response to download the CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=auction_history_report.csv'

        # Create a CSV writer
        writer = csv.writer(response)

        # Write the header row
        writer.writerow([
            'Vehicle', 'Auction ID', 'Start Date', 'End Date', 'Reserve Price', 
            'Total Bids', 'Top Bid Amount', 'Highest Bidder Email', 'On Bid', 'Returned to Available','sold'
        ])

        # Write data rows
        for auction_history in queryset:
            writer.writerow([
                auction_history.vehicle.registration_no,
                auction_history.auction.auction_id,
                auction_history.start_date,
                auction_history.end_date,
                auction_history.reserve_price(),
                auction_history.total_bids(),
                auction_history.top_bid_amount(),
                auction_history.highest_bidder_email(),
                auction_history.on_bid,
                auction_history.returned_to_available
            ])

        return response

    # Set a custom label for the action in the admin interface
    history_report.short_description = "Generate CSV for the selected vehicles in auctions"

    top_bid_amount.short_description = 'Top Bid'
    reserve_price.short_description = 'Reserve Price'
    highest_bidder_email.short_description = 'Highest Bidder Email'
    total_bids.short_description = 'Total Bids'

admin.site.site_header = "RVAS Admin"
admin.site.site_title = "RVAS"
admin.site.index_title = "Welcome to RVAS Admin"