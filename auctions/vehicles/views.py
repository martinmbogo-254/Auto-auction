from django.shortcuts import get_object_or_404, render,redirect
from .models import Vehicle, Bidding, VehicleView, Auction, AuctionHistory
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .forms import BidForm, AuctionForm
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from .filters import VehicleFilter
from django.contrib import messages
from .forms import AuctionForm
from django.utils import timezone


# Create your views here.
def homepage(request):
    return render(request, 'vehicles/home.html')

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
    return render(request, 'vehicles/vehicles.html',context)

def vehicledetail(request, pk):
    vehicle = Vehicle.objects.get(id=pk)
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
def place_bid(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    if request.method == 'POST':
        amount = request.POST.get('amount')
        if int(amount) < vehicle.reserve_price:
            messages.warning(request, 'Bid amount must be at higher than the reserved price.')
            return HttpResponseRedirect(reverse('detail', args=[vehicle_id]))
        Bidding.objects.create(vehicle=vehicle, user=request.user, amount=amount)
        messages.success(request, 'Your bid has been placed successfully!')
        return HttpResponseRedirect(reverse('detail', args=[vehicle_id]))

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