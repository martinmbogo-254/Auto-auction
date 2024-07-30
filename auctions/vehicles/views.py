from django.shortcuts import get_object_or_404, render,redirect
from .models import Vehicle, Bidding, VehicleView, Auction
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .forms import BidForm, AuctionForm
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from .filters import VehicleFilter
from django.contrib import messages

# Create your views here.
def homepage(request):
    return render(request, 'vehicles/home.html')

def vehiclespage(request):
    vehicles = Vehicle.objects.all()
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
                vehicle.bid_status = 'in_auction'  # Update this status based on your needs
                vehicle.save()
            messages.success(request, 'Auction added successfully!')
            return redirect('auctions')
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