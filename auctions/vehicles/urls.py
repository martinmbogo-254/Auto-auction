from django.urls import path
from . import views


urlpatterns = [
    path('',views.homepage, name='homepage' ),
    path('vehicles/',views.vehiclespage, name='vehicles'),
    path('logout/', views.logout_view, name='logout'),
    path('vehicle/<str:registration_no>/',views.vehicledetail, name='detail' ),
    path('place_bid/<int:vehicle_id>/', views.place_bid, name='place_bid'),
    path('add-auction/', views.auction_add, name='auction_add'),
    path('auctions/', views.auction_list, name='auction_list'),
    path('auction/<int:pk>/', views.auction_detail, name='auction_detail'),
    path('administration/',views.admin_dash, name='administration'),
    path('admin/auction-status/', views.auction_status_update, name='auction_status_update'),




]