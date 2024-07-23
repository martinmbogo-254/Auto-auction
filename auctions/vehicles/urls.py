from django.urls import path
from . import views


urlpatterns = [
    path('',views.homepage, name='homepage' ),
    path('vehicles/',views.vehiclespage, name='vehicles'),
    path('logout/', views.logout_view, name='logout'),
    path('vehicle/<int:pk>/',views.vehicledetail, name='detail' ),
    path('place_bid/<int:vehicle_id>/', views.place_bid, name='place_bid'),
]