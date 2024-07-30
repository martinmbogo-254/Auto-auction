from django import forms
from .models import Bidding, Auction,Vehicle
from .fields import CommaSeparatedIntegerField
from .widgets import CommaSeparatedIntegerWidget

class BidForm(forms.ModelForm):
    amount = CommaSeparatedIntegerField(widget=CommaSeparatedIntegerWidget(attrs={'class': 'form-control'}))

    class Meta:
        model = Bidding
        fields = ['amount']

