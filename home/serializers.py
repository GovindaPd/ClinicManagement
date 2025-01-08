from rest_framework import serializers
from .models import User, Clinic, Patient, Prescription, Invoice
from cities_light.models import *
from django.urls import reverse


class UserLoginSerializer(serializers.ModelSerializer):
    # username = serializers.CharField(max_length=50)
    # password = serializers.CharField(max_length=50)
    
    class Meta:
        model = User
        fields = ['username', 'password']
        #read_only_fields = fields



class UserOtpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['otp']


class UserSerializer(serializers.ModelSerializer):
    profile_img_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'custom_id', 'is_doctor', 'profile_img_url', 'phone']

    def get_profile_img_url(self, obj):
        #here obj represent to model that is used by serializer and here is (User) model It is passed automatically by Django REST Framework when calling a method like get_profile_img_url 
        request = self.context.get('request')
        if obj.profile_img:
            return request.build_absolute_uri(obj.profile_img.url)
        return None


class ClinicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinic
        fields = '__all__'


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'
    


class PrescriptionSerializer(serializers.ModelSerializer):
    patient_name = serializers.ReadOnlyField(source='patient.name')
    doctor_name = serializers.ReadOnlyField(source='doctor.name')
    
    class Meta:
        model = Prescription
        fields = '__all__'
    


class RegionSerializers(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['id','name']


class CitySerializers(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id','name']
        