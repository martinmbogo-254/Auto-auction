from django import forms
from .models import Bidding, Auction,Vehicle
from .fields import CommaSeparatedIntegerField
from .widgets import CommaSeparatedIntegerWidget

class BidForm(forms.ModelForm):
    amount = CommaSeparatedIntegerField(widget=CommaSeparatedIntegerWidget(attrs={'class': 'form-control'}))

    class Meta:
        model = Bidding
        fields = ['amount','referred_by']


class AuctionForm(forms.ModelForm):
    vehicles= forms.ModelMultipleChoiceField(
        queryset=Vehicle.objects.filter(status='available'),
        widget=forms.CheckboxSelectMultiple)
    class Meta:
        model = Auction
        fields = ['start_date', 'end_date', 'vehicles', 'approved']
        # widgets = {
        #     'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        #     'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        # }
    
    
class FeedbackForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your name',
            'required': True
        }),
        label='Name'
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email',
            'required': True
        }),
        label='Email'
    )
    feedback = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Write your feedback here',
            'rows': 5,
            'required': True
        }),
        label='Feedback'
    )