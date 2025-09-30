from rest_framework import serializers
from .models import *
from cities_light.models import *
from django.urls import reverse


class RegionSerializers(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['id','name']


class CitySerializers(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id','name']