from django.shortcuts import get_object_or_404, render,redirect
from .models import Vehicle, Bidding, VehicleView, Auction, AuctionHistory,NotificationRecipient,VehicleMake,VehicleModel,ManufactureYear
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .forms import BidForm, AuctionForm
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from .filters import VehicleFilter
from django.contrib import messages
from .forms import AuctionForm,FeedbackForm
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse



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

    # Fetch the available fields dynamically from your model
    makes = VehicleMake.objects.all()
    models = VehicleModel.objects.all()
    years_of_manufacture = ManufactureYear.objects.all()
    transmissions = Vehicle.TRANSMISSION_CHOICES

    paginator = Paginator(vehicles_on_sale,12 )  # Display 12 objects per page

    page = request.GET.get('page')
    try:
        vehicles_on_sale = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        vehicles_on_sale = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        vehicles_on_sale = paginator.page(paginator.num_pages)
    context = {
        'vehicles_on_sale': vehicles_on_sale,
        'vehiclefilter':vehiclefilter,
        'vehicles_count':vehicles_count,
        'vehicles_on_auction' :vehicles_on_auction,
        'on_salecount' :on_salecount,
        'on_auctioncount' :on_auctioncount,
         'makes': makes,
        'models': models,
        'years_of_manufacture': years_of_manufacture,
        'transmissions': transmissions,
        
    }
    return render (request,'vehicles/vehicles.html', context)
from django.http import JsonResponse
from django.shortcuts import render
from .models import Vehicle




def vehicledetail(request, pk):
    vehicle = get_object_or_404(Vehicle, id=pk)
    # Get the vehicle using the slugified registration number
    # vehicle = get_object_or_404(Vehicle, registration_no__iexact=registration_no.replace("-", " "))
    if request.user.is_authenticated:
        # Check if the user has already viewed this vehicle
        if not VehicleView.objects.filter(vehicle=vehicle, user=request.user).exists():
            vehicle.views += 1
            vehicle.save()
            # Record this view
            VehicleView.objects.create(vehicle=vehicle, user=request.user)
    similar_vehicles = Vehicle.objects.filter(make=vehicle.make, model=vehicle.model,is_approved=True).exclude(id=vehicle.id)
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
def place_bid(request, pk):
    vehicle = get_object_or_404(Vehicle, id=pk)
    # Get the vehicle using the slugified registration number
    # vehicle = get_object_or_404(Vehicle, registration_no__iexact=registration_no.replace("-", " "))

    if request.method == 'POST':
        amount = request.POST.get('amount')
        referred_by = request.POST.get('referred_by')
        accept_terms = request.POST.get('accept_terms')

        try:
            amount = int(amount)
        except (ValueError, TypeError):
            messages.error(request, 'Please enter a valid bid amount.')
            return redirect('detail', vehicle.id)

        if not accept_terms:
            messages.error(request, 'You must accept the Terms and Conditions to place a bid.')
            return redirect('detail', vehicle.id)

        # Ensure the bid is above 70% of the reserve price
        min_bid = vehicle.reserve_price * 0.7
        if amount <= min_bid:
            messages.warning(request, f'Your bid must be greater than 70% of the reserve price (Ksh {vehicle.reserve_price:,.0f}).')
            return redirect('detail', vehicle.id)

        # Check the current highest bid
        current_highest_bid = Bidding.objects.filter(vehicle=vehicle,discarded=False).order_by('-amount').first()
        #check if bid is discarded or not 
        # if current_highest_bid.discarded == 'True':
        #     messages.warning(request, f'Another Valid Bid already exists.')
        #     return redirect('detail', vehicle.id)

        if current_highest_bid and amount <= current_highest_bid.amount :
            messages.warning(request, f'Your bid must be higher than the current highest bid.')
            return redirect('detail', vehicle.id)

        # Notify the current highest bidder if they are outbid
        if current_highest_bid:
            send_outbid_notification(current_highest_bid.user, vehicle, current_highest_bid.amount)

        # Create the new bid
        bid = Bidding.objects.create(vehicle=vehicle, user=request.user, amount=amount, referred_by=referred_by)
        messages.success(request, 'Your bid has been placed successfully!')

        # Send "Thank You" email to the bidder
        send_thank_you_notification(bid, vehicle)

        # Send notification email to admin or other recipients
        send_bid_notification(bid, vehicle)

        return redirect('detail', vehicle.id)

    return redirect('detail', vehicle.id)

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
    formatted_amount = f"{bid.amount:,.0f}"
    # Context data for the template
    context = {
        'username': bid.user.username,
        'registration_no': vehicle.registration_no,
        'amount': formatted_amount,  # Formats number with commas
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


def feedback_view(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            # Extract form data
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            feedback = form.cleaned_data['feedback']

            # Prepare email content
            subject_user = "Thank you for your feedback!"
            message_user = (
                f"Hi {name},\n\n"
                "Thank you for taking the time to share your feedback with us. "
                "We truly value your input .\n\n"
                "Best regards,\nYour Team"
            )

            subject_team = f"New Feedback Received from {name}"
            message_team = (
                f"Feedback Details:\n"
                f"-----------------\n"
                f"Name: {name}\n"
                f"Email: {email}\n"
                f"Feedback:\n{feedback}\n"
            )
            
            # Sending emails
            try:
                # Email to the user
                send_mail(
                    subject_user,
                    message_user,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )

                # Fallback email recipients if none are found in the database
                recipient_list = list(NotificationRecipient.objects.values_list('email', flat=True))
                if not recipient_list:
                    recipient_list = ['fuel@riverlong.com']
                # Email to the team
                send_mail(
                    subject_team,
                    message_team,
                    settings.DEFAULT_FROM_EMAIL,
                    recipient_list,  # Your team email
                    fail_silently=False,
                )
                # Success message for the user
                messages.success(request, "Thank you for your feedback! We've received your message.")
            except Exception as e:
                messages.error(request, f"An error occurred while sending your feedback: {e}")

            # Redirect to the feedback page
            return redirect('contactus')
    else:
        form = FeedbackForm()
    
    return render(request, 'vehicles/contactus.html', {'form': form})