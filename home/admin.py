from django.contrib import admin
from .models import *
#from rest_framework.authtoken.models import Token


admin.site.register(User)
admin.site.register(Clinic)
admin.site.register(Patient)
admin.site.register(Prescription)
admin.site.register(Invoice)
