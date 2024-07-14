from django.shortcuts import render,redirect
from .models import Vehicle
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required
# Create your views here.
def homepage(request):
    return render(request, 'vehicles/home.html')

def vehiclespage(request):
    vehicles = Vehicle.objects.all()
    context = {
        'vehicles': vehicles
    }
    return render(request, 'vehicles/vehicles.html',context)

@login_required
def logout_view(request):
    logout(request)
    return redirect('homepage')