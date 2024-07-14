from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm 
from django.contrib.auth import logout


def register(request):
    #redirect a user to the hompage if they are already loged in
    if request.user.is_authenticated:
        return redirect('vehicles')
    else:
        #perform this operation if the user is not logged in
        if request.method == 'POST':
            form = UserRegistrationForm(request.POST)
            if form.is_valid():
                form.save()
                username = form.cleaned_data.get('username')
                messages.success(request, f'Hello {username}, Your account has been successfully created.. !! You can now login ')
                return redirect('login')
        else:
            form = UserRegistrationForm()
        context = {'form': form}
        return render(request, 'users/register.html', context)


