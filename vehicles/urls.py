from django.urls import path
from . import views
from users.views import ResetPasswordView
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('',views.homepage, name='homepage' ),
    # path('vehicles/',views.vehiclespage, name='vehicles'),
    path('available_vehicles/',views.allvehiclespage, name='available_vehicles'),
    path('logout/', views.logout_view, name='logout'),
    path('vehicle/<int:pk>/',views.vehicledetail, name='detail' ),
    path('place_bid/<int:pk>/', views.place_bid, name='place_bid'),
    path('add-auction/', views.auction_add, name='auction_add'),
    path('auctions/', views.auction_list, name='auction_list'),
    path('auction/<int:pk>/', views.auction_detail, name='auction_detail'),
    path('administration/',views.admin_dash, name='administration'),
    path('admin/auction-status/', views.auction_status_update, name='auction_status_update'),
    path('reports/', views.reports, name='reports'),
    path('terms/',views.terms, name='terms'),
    path('aboutus/',views.aboutus, name='aboutus'),
    path('contactus/',views.feedback_view, name='contactus'),
    path('password-reset/', ResetPasswordView.as_view(), name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='users/password/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='users/password/password_reset_complete.html'),
         name='password_reset_complete'),

     # path('get-models-for-make/', views.get_models_for_make, name='get_models_for_make'),
     # path('get-models/<int:make_id>/', views.get_models, name='get_models'),

]