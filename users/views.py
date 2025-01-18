from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm ,ProfileForm
from django.contrib.auth import logout
from .models import Profile
from vehicles.models import Bidding

from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'users/password/password_reset.html'
    email_template_name = 'users/password/password_reset_email.html'
    subject_template_name = 'users/password/password_reset_subject.html'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('homepage')


def register(request):
    # Redirect a user to the homepage if they are already logged in
    if request.user.is_authenticated:
        return redirect('available_vehicles')
    else:
        # Perform this operation if the user is not logged in
        if request.method == 'POST':
            form = UserRegistrationForm(request.POST)
            p_form = ProfileForm(request.POST)
            accept_terms = request.POST.get('accept_terms')  # Check if checkbox is checked

            if not accept_terms:
                messages.error(request, "You must accept the Terms and Conditions to register.")
            elif form.is_valid() and p_form.is_valid():
                user = form.save()
                user.refresh_from_db()
                p_form = ProfileForm(request.POST, instance=user.profile)
                p_form.full_clean()
                p_form.save()
                username = form.cleaned_data.get('username')
                messages.success(request, f'Hello {username}, your account has been successfully created! You can now log in.')
                return redirect('login')
        else:
            form = UserRegistrationForm()
            p_form = ProfileForm()

        context = {
            'form': form,
            'p_form': p_form
        }
        return render(request, 'users/register.html', context)

@login_required
def profile_page(request):
    profile = Profile.objects.get(user=request.user)
    user_bids = Bidding.objects.filter(user=request.user).select_related('vehicle')
    context = {
        'user_bids':user_bids,
        'profile': profile
    }
    return render(request, 'users/profile.html', context)
