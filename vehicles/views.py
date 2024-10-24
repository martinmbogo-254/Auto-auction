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
    context = {
        'upcoming_auctions': upcoming_auctions,
    }
    return render(request, 'vehicles/home.html', context)

def aboutus(request):
    context = {

    }
    return render(request, 'vehicles/aboutus.html', context)

def contactus(request):
    context = {

    }
    return render(request, 'vehicles/contactus.html', context)



def vehiclespage(request):
    vehicles = Vehicle.objects.filter(status='on_auction')
    vehicles_count = vehicles.count()
    vehiclefilter = VehicleFilter(request.GET, queryset=vehicles)
    vehicles = vehiclefilter.qs
    
    context = {
        'vehicles': vehicles,
        'vehiclefilter':vehiclefilter,
        'vehicles_count':vehicles_count
    }
    return render(request, 'vehicles/on_auction.html',context)

def available_vehiclespage(request):
    available_vehicles = Vehicle.objects.filter(status='available')
    context={
        'available_vehicles' :available_vehicles
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
def place_bid(request, registration_no):
    vehicle = get_object_or_404(Vehicle, registration_no=registration_no)
    
    # Check if the user has already placed a bid on this vehicle
    existing_bid = Bidding.objects.filter(vehicle=vehicle, user=request.user).first()

    if existing_bid:
        messages.warning(request, 'You have already placed a bid on this vehicle.')
        return HttpResponseRedirect(reverse('detail', args=[registration_no]))

    if request.method == 'POST':
        amount = request.POST.get('amount')

        # Create a new bid if no previous bid exists for this user on this vehicle
        bid = Bidding.objects.create(vehicle=vehicle, user=request.user, amount=amount)
        messages.success(request, 'Your bid has been placed successfully!')

        # Check if the vehicle is part of an active auction
        current_auction = Auction.objects.filter(vehicles=vehicle, end_date__gte=timezone.now(), approved=True).first()

        # Send email notification after the bid is placed
        send_bid_notification(bid, vehicle, current_auction)

        return HttpResponseRedirect(reverse('detail', args=[registration_no]))

    return HttpResponseRedirect(reverse('detail', args=[registration_no]))


# Function to send email notification when a bid is placed
def send_bid_notification(bid, vehicle, auction=None):  # Now accepts an optional auction argument
    subject = f"New Bid Placed on {vehicle.registration_no}"

    # Check if the vehicle is part of an auction and include auction info in the email
    auction_info = f" (Auction ID: {auction.auction_id})" if auction else ""

    message = (
        f"A new bid has been placed by {bid.user.username} on the vehicle with "
        f"registration number {vehicle.registration_no}{auction_info}.\n\n"
        f"Reserved Price: {vehicle.reserve_price}.\n"
        f"Bid Amount: {bid.amount}\n"
        f"User Email: {bid.user.email}\n"
        f"Vehicle: {vehicle.make} {vehicle.model}\n"
    )
    from_email = settings.DEFAULT_FROM_EMAIL
 # Fetch dynamic recipient emails from the database
    recipient_list = list(NotificationRecipient.objects.values_list('email', flat=True))
    
    # Fallback to a default email if no recipients are found
    if not recipient_list:
        recipient_list = ['fuel@riverlong.com']  # Replace with a fallback email
    
    send_mail(subject, message, from_email, recipient_list, fail_silently=False)

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