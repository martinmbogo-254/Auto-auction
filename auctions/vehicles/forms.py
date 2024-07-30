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
    class Meta:
        model = Auction
        fields = ['start_date', 'end_date', 'vehicles', 'approved']
        widgets = {
            'vehicles': forms.CheckboxSelectMultiple(),
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super(AuctionForm, self).__init__(*args, **kwargs)
        # Filter vehicles to only show those that are available
        self.fields['vehicles'].queryset = Vehicle.objects.filter(status='available')
