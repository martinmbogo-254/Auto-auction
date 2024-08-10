from django import forms
from .models import Bidding, Auction,Vehicle
from .fields import CommaSeparatedIntegerField
from .widgets import CommaSeparatedIntegerWidget

class BidForm(forms.ModelForm):
    amount = CommaSeparatedIntegerField(widget=CommaSeparatedIntegerWidget(attrs={'class': 'form-control'}))

    class Meta:
        model = Bidding
        fields = ['amount']


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
    
    
