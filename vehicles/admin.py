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
from .models import (
    VehicleImage, VehicleMake, VehicleModel, 
    ManufactureYear, FuelType, VehicleBody, Vehicle, Bidding, Auction, VehicleView, AuctionHistory,NotificationRecipient,Financier,Yard,AwardHistory
)


from django.contrib import admin
from django.http import HttpResponse
import csv
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

# Add a description to the custom action
@admin.register(AwardHistory)
class AwardHistoryAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'user_full_name', 'user_email', 'amount', 'awarded_at')
    search_fields = ('vehicle__registration_no', 'user__username', 'user__email')
    list_filter = ('awarded_at',)

    def user_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    user_full_name.short_description = 'User Full Name'

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'

    def amount(self, obj):
        return f"Ksh {obj.amount:,}"
    amount.short_description = 'Amount'

    # Optional: Customize the ordering of the records
    ordering = ('-awarded_at',)

@admin.register(Bidding)
class BidAdmin(admin.ModelAdmin):
    search_fields = ('vehicle__registration_no', 'user__username')
    list_display = ('vehicle', 'user_full_name', 'user_email','awarded' ,'formatted_amount', 'bid_time')
    actions = ['generate_bid_report','award_bid']

    # Method to extract user's full name (first_name + last_name)
    def user_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

    user_full_name.short_description = 'User Full Name'  # This sets the column name in the admin list view

    # Method to extract user's email
    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = 'User Email'  # This sets the column name in the admin list view

    # Method to format the 'amount' field with thousands separator
    def formatted_amount(self, obj):
        return '{:,.0f}'.format(obj.amount)

    formatted_amount.short_description = 'Amount'  # This sets the column name in the admin list view

    def award_bid(self, request, queryset):
        # Ensure only one bid is selected
        if queryset.count() != 1:
            self.message_user(
                request,
                "Please select exactly one bid to award.",
                level=messages.WARNING
            )
            return

        bid = queryset.first()

        # Check if the vehicle already has an awarded bid
        # if bid.vehicle.bids.filter(awarded=True).exists():
        #     self.message_user(
        #         request,
        #         f"The bid for vehicle {bid.vehicle.registration_no} has already been awarded.",
        #         level=messages.WARNING
        #     )
        #     return

        # if bid.awarded:
        #     self.message_user(
        #         request,
        #         f"The bid for vehicle {bid.vehicle.registration_no} is already awarded.",
        #         level=messages.WARNING
        #     )
        #     return
        vehicle = Vehicle.objects.select_for_update().get(pk=bid.vehicle.pk)
                
        # Check if any bid for this vehicle is already awarded
        existing_awarded_bid = Bidding.objects.select_for_update().filter(
            vehicle=vehicle,
            awarded=True
        ).first()
        
        if existing_awarded_bid:
            if existing_awarded_bid.pk == bid.pk:
                self.message_user(
                    request,
                    f"This bid is already awarded.",
                    level=messages.WARNING
                )
            else:
                self.message_user(
                    request,
                    f"Vehicle {vehicle.registration_no} already has an awarded bid to "
                    f"{existing_awarded_bid.user.get_full_name()} for "
                    f"Ksh {'{:,.0f}'.format(existing_awarded_bid.amount)}.",
                    level=messages.WARNING
                )
            return
        # Mark the bid as awarded
        bid.awarded = True
        bid.save()

        # Update the associated vehicle's status
        bid.vehicle.status = 'bid_won'
        bid.vehicle.save()

        # Create an entry in the AwardHistory model
        try:
            AwardHistory.objects.create(
                user=bid.user,
                vehicle=bid.vehicle,
                amount=bid.amount,
                awarded_at=bid.bid_time
            )
        except Exception as e:
            self.message_user(
                request,
                f"Failed to update award history. Error: {e}",
                level=messages.ERROR
            )
            return

        # Send notification email to the user
        try:
            context = {
                'first_name': bid.user.first_name,
                'registration_no': bid.vehicle.registration_no,
                'bid_details_url': 'your-bid-details-url-here',  # Replace with actual URL to bid details page
            }

            # Render the HTML email content from the template
            email_subject = "Bid Awarded"
            email_message = render_to_string(
                'vehicles/emails/bid_award.html',  # Path to the email HTML template
                context
            )

            # Send the email
            send_mail(
                subject=email_subject,
                message=email_message,  # The plain-text message (optional as we're sending HTML email)
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[bid.user.email],
                fail_silently=False,
                html_message=email_message  # HTML content of the email
            )

            return "Notification email sent to the user."
        except Exception as e:
            email_status = f"Notification email failed to send. Error: {e}"

        # Notify the admin about the success of the operation
        self.message_user(
            request,
            f"The bid for vehicle {bid.vehicle.registration_no} has been successfully awarded. {email_status}",
            level=messages.SUCCESS
        )

    award_bid.short_description = "Award selected bid"
    # CSV export function (modified to include user details)
    def generate_bid_report(self, request, queryset):
        # Create the HttpResponse object with the appropriate CSV header
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="bid_report.csv"'
        writer = csv.writer(response)
        
        # Write header row with columns
        writer.writerow(['vehicle', 'user_full_name', 'user_email', 'amount', 'bid_time','awarded'])

        # Write rows with the relevant data
        for bid in queryset:
            writer.writerow([
                bid.vehicle.registration_no,  # Vehicle registration number
                f"{bid.user.first_name} {bid.user.last_name}",  # User's full name
                bid.user.email,  # User's email
                self.formatted_amount(bid),
                bid.bid_time , # Bid time
                bid.awarded # Awarded status
            ])
        
        return response

    generate_bid_report.short_description = "Generate bid report for selected vehicles"
# @admin.register(Bidding)
# class BidAdmin(admin.ModelAdmin):
#     search_fields = ('vehicle__registration_no', 'user__username')
#     list_display = ('vehicle', 'user', 'formatted_amount', 'bid_time')
#     actions = ['generate_bid_report']
#     readonly_fields = ('vehicle', 'user', 'amount')

#     # Format the amount field with thousands separator
#     def formatted_amount(self, obj):
#         # Format the amount with thousands separator
#         return '{:,.0f}'.format(obj.amount)

#     formatted_amount.short_description = 'Amount'  # Column name in the admin interface

#     # CSV export function (without formatting, raw data)
#     def generate_bid_report(self, request, queryset):
#         # Create the HttpResponse object with the appropriate CSV header.
#         response = HttpResponse(content_type='text/csv')
#         response['Content-Disposition'] = 'attachment; filename="bid_report.csv"'
#         writer = csv.writer(response)
#         writer.writerow(['vehicle', 'user', 'amount', 'bid_time'])

#         for bid in queryset:
#             writer.writerow([
#                 bid.vehicle.registration_no,
#                 bid.user.username,
#                 self.formatted_amount(bid),
#                 # bid.formatted_amount,  # Raw amount for the CSV file
#                 bid.bid_time
#             ])
        
#         return response

#     generate_bid_report.short_description = "Generate bid report for selected vehicles"
class VehicleImageInline(admin.TabularInline):
    model = VehicleImage
    extra = 1  # Number of empty forms to display

class BidInline(admin.TabularInline):
    model = Bidding
    readonly_fields = ('user', 'amount', 'bid_time',)  
    # extra = 1  
    can_delete = False

class VehicleViewInline(admin.TabularInline):
    model = VehicleView
    # extra = 1 
    readonly_fields=('vehicle','user','viewed_at')
    can_delete = False


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    # Custom formatted methods
    def formatted_reserve_price(self, obj):
        # Format the reserve price with thousands separator
        return '{:,.0f}'.format(obj.reserve_price)
    formatted_reserve_price.short_description = 'Reserve Price'

    def formatted_mileage(self, obj):
        # Format the mileage with thousands separator
        return '{:,.0f}'.format(obj.mileage) if obj.mileage is not None else 'N/A'
    formatted_mileage.short_description = 'Mileage'

    def formatted_views(self, obj):
        # Format the views with thousands separator
        return '{:,.0f}'.format(obj.views)
    formatted_views.short_description = 'Views'

    # Ensure you're using the correct method names in list_display
    list_display = (
        'registration_no', 'Financier', 'make', 'model', 'YOM', 'formatted_mileage', 'engine_cc', 
        'body_type', 'color', 'yard', 'fuel_type', 'is_approved', 'status', 'formatted_reserve_price', 
        'is_hotsale', 'created_at', 'updated_at', 'days_since_creation', 'current_auction_end_date', 'formatted_views'
    )

    # Other configurations
    search_fields = ('make__name', 'registration_no', 'model__name', 'YOM__year', 'status')
    list_filter = ('status', 'make', 'model', 'YOM', 'body_type', 'fuel_type', 'created_at', 'updated_at', 'is_approved')
    inlines = [VehicleImageInline, BidInline, VehicleViewInline]
    readonly_fields = ('views', 'status', 'approved_by', 'approved_at', 'is_approved')
    actions = ['make_available', 'generate_vehicle_report', 'sell', 'approve_vehicle']

    # Custom action for generating reports
    def generate_vehicle_report(self, request, queryset):
        from django.http import HttpResponse
        import csv
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="vehicle_report.csv"'

        writer = csv.writer(response)
        writer.writerow(['Registration No', 'Financier', 'Make', 'Model', 'Year of Manufacture', 'Mileage', 'Transmission', 'Engine CC', 'Body Type', 'Seats', 'Color', 'Fuel Type', 'Storage Yard', 'Reserve Price', 'Status', 'Days Since Creation'])

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

    # Admin action for marking vehicles as available
    def make_available(self, request, queryset):
        updated = queryset.update(status='available')
        self.message_user(request, f"{updated} vehicle(s) successfully marked as available.")
    make_available.short_description = "Mark selected vehicles as available"

    # Admin action for selling vehicles
    def sell(self, request, queryset):
        updated = queryset.update(status='sold')
        self.message_user(request, f"{updated} vehicle(s) successfully sold")
    sell.short_description = "Mark selected vehicles as sold"

    # Get auction end date for the vehicle
    def current_auction_end_date(self, obj):
        return obj.current_auction_end_date()
    current_auction_end_date.short_description = 'Auction End Date'

    # Admin action for approving vehicles
    def approve_vehicle(self, request, queryset):
        if not request.user.groups.filter(name='Admins').exists():
            self.message_user(request, "Only Admins can approve vehicles.", level=messages.WARNING)
            return

        count = 0
        for vehicle in queryset.filter(is_approved=False):
            vehicle.approve(request.user)
            count += 1

        self.message_user(request, f"{count} vehicle(s) have been approved.", level=messages.SUCCESS)
    approve_vehicle.short_description = "Approve selected vehicles"

# admin.site.register(VehicleAdmin)

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
    search_fields = ('vehicles__registration_no','auction_id')
    filter_horizontal = ('vehicles',)
    list_filter = ('approved',EndedFilter,'start_date', 'end_date','created_at')
    inlines = [AuctionHistoryInline]
    readonly_fields = ('approved','processed','approved_by','approved_at')
    actions = ['update_vehicle_status','approve_auction','disapprove_auction']

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

    # Custom admin action to approve auctions
    def approve_auction(modeladmin, request, queryset):
        # Check if the user is part of the 'Approvers' group
        if not request.user.groups.filter(name='Approvers').exists():
            modeladmin.message_user(request, "You do not have permission to approve auctions.", level='error')
            return
        
        # Check if the auction is already approved
        already_approved = queryset.filter(approved=True)
        if already_approved.exists():
            modeladmin.message_user(request, f"{already_approved.count()} auction(s) already approved.", level='error')
            return  # Do nothing if any of the selected auctions are already approved
        
        # Approve all selected auctions
        queryset.update(approved=True)
        modeladmin.message_user(request, f"{queryset.count()} auction(s) approved successfully.")

    approve_auction.short_description = "Approve selected auctions"

    # Custom admin action to disapprove auctions
    def disapprove_auction(modeladmin, request, queryset):
        # Check if the user is part of the 'Approvers' group
        if not request.user.groups.filter(name='Approvers').exists():
            modeladmin.message_user(request, "You do not have permission to disapprove auctions.", level='error')
            return
        
        # Disapprove all selected auctions
        queryset.update(approved=False)
        modeladmin.message_user(request, f"{queryset.count()} auction(s) disapproved successfully.")

    disapprove_auction.short_description = "Disapprove selected auctions"

    def update_vehicle_status(self, request, queryset):
        now = timezone.now()
        for auction in queryset:
            if auction.end_date <= now and auction.approved:
                for vehicle in auction.vehicles.all():
                    # Get the highest bid for the vehicle
                    highest_bid = vehicle.bidding.order_by('-amount').first()
                    if highest_bid and highest_bid.amount >= vehicle.reserve_price:
                        vehicle.status = 'bid_won'
                        # Send an email to the winner
                        self.send_winner_email(highest_bid)
                    else:
                        vehicle.status = 'available'
                    vehicle.save()
                
                self.message_user(request, f"Updated vehicle statuses for auction {auction.auction_id}", level=messages.SUCCESS)
            else:
                self.message_user(request, f"Auction {auction.auction_id} is not yet ended or not approved.", level=messages.ERROR)
    update_vehicle_status.short_description = "Complete Selected Auctions"

  
    def send_winner_email(self, winning_bid):
        # Context data for the template
        context = {
            'username': winning_bid.user.username,
            'registration_no': winning_bid.vehicle.registration_no,
            'amount': "{:,.2f}".format(winning_bid.amount),  # Formats number with commas
            'email': winning_bid.user.email
        }
        
        # Render the HTML content
        html_message = render_to_string('vehicles/emails/bidwin.html', context)
        
        # Create plain text version for email clients that don't support HTML
        plain_message = strip_tags(html_message)
        
        subject = f"Congratulations! You've won the bid for {winning_bid.vehicle.registration_no}"
    
        # Send email with both HTML and plain text versions
        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[winning_bid.user.email],
            fail_silently=False
        )
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

admin.site.site_header = "Autobid Admin"
admin.site.site_title = "Riverlong Autobid"
admin.site.index_title = "Welcome to Autobid Admin"