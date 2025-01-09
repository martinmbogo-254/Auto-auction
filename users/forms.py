
from django import forms
from django.contrib.auth.models import User
from .models import Profile

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile



class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()
    accept_terms = forms.BooleanField(
        required=True,
        label="I accept the Terms and Conditions",
        error_messages={'required': "You must accept the Terms and Conditions to register."}
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'accept_terms']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email
class ProfileForm(forms.ModelForm):

    class Meta:
        
        model = Profile
        fields = ['phone_number','ID_number','location']
       

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']