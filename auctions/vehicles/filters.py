import django_filters
from django_filters import CharFilter
from .models import *


class VehicleFilter(django_filters.FilterSet):
    
    # name=CharFilter(field_name='name', lookup_expr='icontains')
    class Meta:
        model = Vehicle
        fields = {'make','model','YOM','body_type'}