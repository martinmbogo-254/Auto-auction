from django import forms
from .models import Bidding

class BidForm(forms.ModelForm):

    class Meta:
        model = Bidding
        fields = ['amount',]