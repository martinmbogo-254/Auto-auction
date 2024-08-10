import django_filters
from django_filters import CharFilter
from .models import *


class VehicleFilter(django_filters.FilterSet):
    
    # name=CharFilter(field_name='name', lookup_expr='icontains')
    class Meta:
        model = Vehicle
        fields = {'make','model','YOM','body_type','engine_cc','fuel_type'}

    def __init__(self, *args, **kwargs):
        super(VehicleFilter, self).__init__(*args, **kwargs)
        for field_name, field in self.filters.items():
            field.field.widget.attrs.update({'class': 'form-control'})