from django.shortcuts import get_object_or_404, render,redirect
from .models import Vehicle, Bidding
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .forms import BidForm
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
    
    biddings = Bidding.objects.filter(vehicle=vehicle)
    context = {
       'vehicle': vehicle,
       'biddings':biddings,
       
    }
    return render(request, 'vehicles/details.html', context)
@login_required(login_url='login')
def place_bid(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    if request.method == 'POST':
        amount = request.POST.get('amount')
        Bidding.objects.create(vehicle=vehicle, user=request.user, amount=amount)
        messages.success(request, 'Your bid has been placed successfully!')
        return HttpResponseRedirect(reverse('detail', args=[vehicle_id]))
    

# @login_required(login_url='login')
# def Bid(request, pk):
#     # getting post objects by their id
#     vehicle = get_object_or_404(Vehicle, id=pk)
#     user = request.user
#     # form method
#     if request.method == 'POST':
#         form = BidForm(request.POST)
#         # validating the form.
#         if form.is_valid():
#             bid = form.save(commit=False)
#             bid.vehicle = vehicle
#             bid.user = user
#             bid.save()
#             messages.success(request, 'Your bid has been placed successfully!')
#             return HttpResponseRedirect(reverse('detail', args=[pk]))
#     else:
#         form = BidForm()
#     context = {
#         'form': form,
#         'vehicle': vehicle,
#     }
    # return render(request, 'vehicles/bid.html', context)
@login_required
def logout_view(request):
    logout(request)
    return redirect('homepage')