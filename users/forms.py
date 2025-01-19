
from django import forms
from django.contrib.auth.models import User
from .models import Profile
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


class CustomLoginForm(forms.Form):
    username = forms.EmailField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your email address',
            'class': 'form-control'
        })
    )
 
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter your password',
            'class': 'form-control'
        })
    )
    class Meta:
        fields = ['username', 'password']

class UserRegistrationForm(UserCreationForm):
    accept_terms = forms.BooleanField(
        required=True,
        label="I accept the Terms and Conditions",
        error_messages={'required': "You must accept the Terms and Conditions to register."}
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your first name',
            'class': 'form-control'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your last name',
            'class': 'form-control'
        })
    )
    # email = forms.EmailField(
    #     max_length=254,
    #     required=True,
    #     widget=forms.EmailInput(attrs={
    #         'placeholder': 'Enter your email',
    #         'class': 'form-control'
    #     })
    # )
    username = forms.EmailField(  # Changed to EmailField
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your email',
            'class': 'form-control'
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter your password',
            'class': 'form-control'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm your password',
            'class': 'form-control'
        })
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2','accept_terms']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['username']  # Set email same as username
        if commit:
            user.save()
        return user

# class UserRegistrationForm(UserCreationForm):
#     email = forms.EmailField()


#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password1', 'password2', 'accept_terms']

#     def clean_email(self):
#         email = self.cleaned_data.get('email')
#         if User.objects.filter(email=email).exists():
#             raise forms.ValidationError("An account with this email already exists.")
#         return email
class ProfileForm(forms.ModelForm):

    class Meta:
        
        model = Profile
        fields = ['phone_number','ID_number','location']
       

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']