from django.shortcuts import get_object_or_404, render,redirect
from .models import Vehicle, Bidding, VehicleView, Auction, AuctionHistory,NotificationRecipient
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .forms import BidForm, AuctionForm
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from .filters import VehicleFilter
from django.contrib import messages
from .forms import AuctionForm
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def reports(request):
    vehicles = Vehicle.objects.all()
    total_vehicles = vehicles.count()
    context = {
        'total_vehicles': total_vehicles,
       
    }
    return render(request, 'Admin/reports.html', context)
# Create your views here.
def homepage(request):
    upcoming_auctions = Vehicle.objects.filter(status='available')
    hotsale = Vehicle.objects.filter(is_hotsale =True,status='available')
    context = {
        'upcoming_auctions': upcoming_auctions,
        'hotsale':hotsale
    }
    return render(request, 'vehicles/home.html', context)

def aboutus(request):
    context = {

    }
    return render(request, 'vehicles/aboutus.html', context)

def terms(request):
    context = {

    }
    return render(request, 'vehicles/t&c.html', context)

def contactus(request):
    context = {

    }
    return render(request, 'vehicles/contactus.html', context)


def allvehiclespage(request):
    all_vehicles = Vehicle.objects.all()
    vehicles_count = all_vehicles.count()
    vehiclefilter = VehicleFilter(request.GET, queryset=Vehicle.objects.all())
    vehicles_on_sale = vehiclefilter.qs.filter(status="available")
    vehicles_on_auction = vehiclefilter.qs.filter(status='on_auction')
    on_salecount = vehicles_on_sale.count()
    on_auctioncount = vehicles_on_auction.count()
    context = {
        'vehicles_on_sale': vehicles_on_sale,
        'vehiclefilter':vehiclefilter,
        'vehicles_count':vehicles_count,
        'vehicles_on_auction' :vehicles_on_auction,
        'on_salecount' :on_salecount,
        'on_auctioncount' :on_auctioncount,
    }
    return render (request,'vehicles/vehicles.html', context)

def vehicledetail(request, registration_no):
    vehicle = get_object_or_404(Vehicle, registration_no=registration_no)
    if request.user.is_authenticated:
        # Check if the user has already viewed this vehicle
        if not VehicleView.objects.filter(vehicle=vehicle, user=request.user).exists():
            vehicle.views += 1
            vehicle.save()
            # Record this view
            VehicleView.objects.create(vehicle=vehicle, user=request.user)
    similar_vehicles = Vehicle.objects.filter(make=vehicle.make, model=vehicle.model).exclude(id=vehicle.id)
    biddings = Bidding.objects.filter(vehicle=vehicle)
    highest_bid = vehicle.bidding.order_by('-amount').first()
    context = {
       'vehicle': vehicle,
       'biddings':biddings,
       'days_since_creation': vehicle.days_since_creation(),
       'similar_vehicles': similar_vehicles,       
        'highest_bid': highest_bid,
       'similar_vehicles': similar_vehicles,
    }
    return render(request, 'vehicles/details.html', context)
@login_required(login_url='login')
@login_required(login_url='login')
def place_bid(request, registration_no):
    vehicle = get_object_or_404(Vehicle, registration_no=registration_no)

    if request.method == 'POST':
        amount = request.POST.get('amount')
        accept_terms = request.POST.get('accept_terms')

        try:
            amount = int(amount)
        except (ValueError, TypeError):
            messages.error(request, 'Please enter a valid bid amount.')
            return redirect('detail', registration_no=registration_no)

        if not accept_terms:
            messages.error(request, 'You must accept the Terms and Conditions to place a bid.')
            return redirect('detail', registration_no=registration_no)

        if amount <= vehicle.reserve_price:
            messages.warning(request, f'Your bid must be higher than the reserve price of Ksh {vehicle.reserve_price:,}.')
            return redirect('detail', registration_no=registration_no)

        # Check the current highest bid
        current_highest_bid = Bidding.objects.filter(vehicle=vehicle).order_by('-amount').first()

        if current_highest_bid and amount <= current_highest_bid.amount:
            messages.warning(request, f'Your bid must be higher than the current highest bid of Ksh {current_highest_bid.amount:,}.')
            return redirect('detail', registration_no=registration_no)

        # Notify the current highest bidder if they are outbid
        if current_highest_bid:
            send_outbid_notification(current_highest_bid.user, vehicle, current_highest_bid.amount)

        # Create the new bid
        bid = Bidding.objects.create(vehicle=vehicle, user=request.user, amount=amount)
        messages.success(request, 'Your bid has been placed successfully!')

        # Send "Thank You" email to the bidder
        send_thank_you_notification(bid, vehicle)

        # Send notification email to admin or other recipients
        send_bid_notification(bid, vehicle)

        return redirect('detail', registration_no=registration_no)

    return redirect('detail', registration_no=registration_no)

# @login_required(login_url='login')
# def place_bid(request, registration_no):
#     vehicle = get_object_or_404(Vehicle, registration_no=registration_no)

#     # Check if the user has already placed a bid on this vehicle
#     # existing_bid = Bidding.objects.filter(vehicle=vehicle, user=request.user).first()

#     # if existing_bid:
#     #     messages.warning(request, 'You have already placed a bid on this vehicle.')
#     #     return redirect('detail', registration_no=registration_no)

#     if request.method == 'POST':
#         amount = request.POST.get('amount')
#         accept_terms = request.POST.get('accept_terms')  # Check if the checkbox is selected

#         if not accept_terms:
#             messages.error(request, 'You must accept the Terms and Conditions to place a bid.')
#             return redirect('detail', registration_no=registration_no)

#         # Create a new bid if no previous bid exists for this user on this vehicle
#         bid = Bidding.objects.create(vehicle=vehicle, user=request.user, amount=amount)
#         messages.success(request, 'Your bid has been placed successfully!')

#         # Send "Thank You" email to the bidder
#         send_thank_you_notification(bid, vehicle)

#         # Send notification email to admin or other recipients
#         send_bid_notification(bid, vehicle)

#         return redirect('detail', registration_no=registration_no)

#     return redirect('detail', registration_no=registration_no)

# Function to send a thank-you email specifically to the bidder
# def send_thank_you_notification(bid, vehicle):
#     subject = "Thank You for Placing Your Bid!"
#     message = (
#         f"Dear {bid.user.username},\n\n"
#         f"Thank you for placing a bid on the vehicle with registration number {vehicle.registration_no}.\n\n"
#         f"Here are the details of your bid:\n"
#         # f"Reserved Price: {vehicle.reserve_price}\n"
#         f"Bid Amount: {bid.amount}\n"
#         f"Vehicle: {vehicle.make} {vehicle.model}\n\n"
#         f"We appreciate your interest, and we will notify you if your bid is successful.\n\n"
#         f"Best regards,\n"
#         f"Riverlong Team"
#     )
    
#     from_email = settings.DEFAULT_FROM_EMAIL
#     recipient_list = [bid.user.email]

#     send_mail(subject, message, from_email, recipient_list, fail_silently=False)
def send_outbid_notification(user, vehicle, amount):
    """
    Send a notification to the previous highest bidder informing them they have been outbid.

    Args:
        user (User): The user who has been outbid.
        vehicle (Vehicle): The vehicle associated with the bid.
        amount (int): The amount of the outbid.
    """
    subject = f"You've been outbid on {vehicle.registration_no}"
# Format the amount in thousands
    formatted_amount = f"{amount:,.0f}"
    # Prepare context for the email template
    context = {
        'user': user,
        'vehicle': vehicle,
        'amount': formatted_amount,
    }

    # Render the HTML message using the template
    html_message = render_to_string('vehicles/emails/outbid_notification.html', context)

    # Send the email
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_email = user.email
    send_mail(
        subject,
        '',  # Plain text message (can be empty or optional)
        from_email,
        [recipient_email],
        html_message=html_message,
        fail_silently=False,
    )



def send_thank_you_notification(bid, vehicle):
    # Context data for the template
    context = {
        'username': bid.user.username,
        'registration_no': vehicle.registration_no,
        'amount': bid.amount,  # Formats number with commas
        'make': vehicle.make,
        'model': vehicle.model
    }
    
    # Render the HTML content
    html_message = render_to_string('vehicles/emails/bid_confirmation.html', context)
    
    # Create plain text version for email clients that don't support HTML
    plain_message = strip_tags(html_message)
    
    subject = "Thank You for Placing Your Bid!"
    
    # Send email with both HTML and plain text versions
    send_mail(
        subject=subject,
        message=plain_message,
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[bid.user.email],
        fail_silently=False
    )
# Function to send email notification when a bid is placed
# def send_bid_notification(bid, vehicle, auction=None):  # Now accepts an optional auction argument
#     subject = f"New Bid Placed on {vehicle.registration_no}"

#     # Check if the vehicle is part of an auction and include auction info in the email
#     auction_info = f" (Auction ID: {auction.auction_id})" if auction else ""

#     message = (
#         f"A new bid has been placed by {bid.user.username} on the vehicle with "
#         f"registration number {vehicle.registration_no}{auction_info}.\n\n"
#         f"Reserved Price: {vehicle.reserve_price}.\n"
#         f"Bid Amount: {bid.amount}\n"
#         f"User Email: {bid.user.email}\n"
#         f"Vehicle: {vehicle.make} {vehicle.model}\n"
#     )
#     from_email = settings.DEFAULT_FROM_EMAIL
#  # Fetch dynamic recipient emails from the database
#     recipient_list = list(NotificationRecipient.objects.values_list('email', flat=True))
    
#     # Fallback to a default email if no recipients are found
#     if not recipient_list:
#         recipient_list = ['fuel@riverlong.com']  # Replace with a fallback email
    
#     send_mail(subject, message, from_email, recipient_list, fail_silently=False)
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

def send_bid_notification(bid, vehicle, auction=None):
    subject = f"New Bid Placed on {vehicle.registration_no}"

    # Check if the vehicle is part of an auction and include auction info in the email
    auction_info = f" (Auction ID: {auction.auction_id})" if auction else ""

    # Prepare context for the email template
    context = {
        'bid': bid,
        'vehicle': vehicle,
        'auction': auction,
    }

    # Render the HTML message using the template
    html_message = render_to_string('vehicles/emails/bid_notification.html', context)

    # Fallback email recipients if none are found in the database
    recipient_list = list(NotificationRecipient.objects.values_list('email', flat=True))
    if not recipient_list:
        recipient_list = ['fuel@riverlong.com']

    # Send the email
    from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(
        subject,
        '',  # Plain text message (can be empty or optional)
        from_email,
        recipient_list,
        html_message=html_message,
        fail_silently=False,
    )

def auction_add(request):
    if request.method == 'POST':
        form = AuctionForm(request.POST)
        if form.is_valid():
            auction = form.save()
            # Get the selected vehicles from the form
            selected_vehicles = form.cleaned_data['vehicles']
            # Update the bid_status of selected vehicles
            for vehicle in selected_vehicles:
                vehicle.status = 'on_auction'  # Update this status based on your needs
                vehicle.save()
                AuctionHistory.objects.create(
                    vehicle=vehicle,
                    auction=auction,
                    start_date=auction.start_date,
                    end_date=auction.end_date,
                    sold=False)
            messages.success(request, 'Auction added successfully!')
            return redirect('auction_list')
    else:
        form = AuctionForm()
    return render(request, 'admin/create_auction.html', {'form': form})   

def auction_list(request):
    auctions = Auction.objects.all()
    return render(request, 'admin/auctions.html', {'auctions': auctions})


def auction_detail(request, pk):
    auction = get_object_or_404(Auction, pk=pk)
    return render(request, 'admin/auction_details.html', {'auction': auction})

@login_required
def logout_view(request):
    logout(request)
    return redirect('homepage')

# Admin views
@login_required
def admin_dash(request):
    vehicles = Vehicle.objects.all()
    auctions = Auction.objects.all()
    auction_count = auctions.count()
    vehicle_count = vehicles.count()
    context = {
        'vehicle_count': vehicle_count,
        'auction_count': auction_count,
    }
    return render(request, 'admin/dashboard.html', context)


def auction_status_update(request):
    now = timezone.now()
    active_auctions = Auction.objects.filter(end_date__gt=now, approved=True)
    data = {
        'active_auctions_count': active_auctions.count()
    }
    return JsonResponse(data)