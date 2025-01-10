from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now

from cities_light.models import Region, City
from random import randint
import random
import string
import os



def rename_image(instance, filename):
    extension = os.path.splitext(filename)[1]
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    new_name = f"{random_string}_{now().strftime('%d%m%Y%H%M%S')}{extension}"
    
    if isinstance(instance, User):
        return os.path.join('profile_img/', new_name)
    else:   #isinstance(instance, Patient):
        return os.path.join('reports/', new_name)


class User(AbstractUser):
    custom_id       = models.CharField(max_length=10, unique=True)
    is_admin        = models.BooleanField(default=False)
    is_new_staff    = models.BooleanField(default=False)
    otp             = models.CharField(max_length=5, blank=True, null=True)
    is_password_reset = models.BooleanField(default=False)
    profile_img     = models.ImageField(upload_to=rename_image, blank=True)  
    is_password_reset = models.BooleanField(default=False)
    

    # phone = models.CharField(max_length=10, blank=True)
    # token = models.CharField(max_length=255, null=True, blank=True, default="")

    @staticmethod
    def generate_custom_id():
        while True:
            custom_id = randint(100000, 999999)
            if not User.objects.filter(custom_id=custom_id).exists():
                return custom_id
            
    def save(self, *args, **kwargs):
        if not self.custom_id:
            self.custom_id = self.generate_custom_id()
        super(User, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.username}"

        

class Clinic(models.Model):
    user    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clinic')
    name    = models.CharField(max_length=255, help_text="Clinic Name")
    address = models.CharField(max_length=255, blank=True)
    city    = models.ForeignKey(City, on_delete=models.SET_NULL, related_name="clinics_in_city", null=True, blank=True, max_length=255)
    state   = models.ForeignKey(Region, on_delete=models.SET_NULL, related_name="clinics_in_state", null=True, blank=True, max_length=255)
    pincode = models.CharField(max_length=6, null=True, blank=True)
    number  = models.CharField(max_length=15, blank=True)
    email   = models.EmailField(max_length=50, blank=True, null=True)
    
    specializations = models.TextField(blank=True, null=True)
    created_at = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.name}"


# class Staff(models.Model):
#     clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='staffs')
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='users')

#     def __str__(self):
#         return f"Clinic name is {self.clinic.name} username is {self.user.usernaem}"
    


class Patient(models.Model):
    doctor      = models.ForeignKey(User, related_name="patients", on_delete=models.CASCADE)
    clinic      = models.ForeignKey(Clinic, related_name='patients', on_delete=models.CASCADE )
    name        = models.CharField(max_length=255)
    age         = models.PositiveIntegerField(blank=True, null=True)
    gender      = models.CharField(max_length=10, choices=(("Male", "Male"), ("Female", "Female"), ("Other", "Other")), null=True, blank=True)
    number      = models.CharField(max_length=15, blank=True, null=True)
    address     = models.CharField(max_length=255, blank=True, null=True)
    medical_history = models.TextField(blank=True)
    image       = models.ImageField(upload_to=rename_image, blank=True)
    created_at  = models.DateField(auto_now=True)   

    def __str__(self):
        return f"{self.name}"



class Prescription(models.Model):
    patient     = models.ForeignKey(Patient, related_name="records", on_delete=models.CASCADE)
    symptoms    = models.TextField(blank=True)
    prescription = models.TextField(blank=True)
    image       = models.ImageField(upload_to='rename_image', blank=True)
    visit_date  = models.DateTimeField(auto_now=True)
    next_visit  = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.patient.name


class Invoice(models.Model):
    PAYMENT_STATUS = (
        ('Paid', 'Paid'),
        ('Pending', 'Pending'),
        ('Partial Paid', 'Partial Paid'),
        )
    prescription = models.OneToOneField(Prescription, on_delete=models.CASCADE, related_name='invoice', null=True, blank=True)
    amount          = models.IntegerField(default=0)
    remainig_amount = models.IntegerField(default=0)
    status          = models.CharField(max_length=15, choices=PAYMENT_STATUS, default='Paid')

    def __str__(self):
        return self.amount




# class MedicalRecord(models.Model):
#     patient = models.ForeignKey(Patient, related_name="records", on_delete=models.CASCADE)
#     doctor = models.ForeignKey(User, related_name="records", on_delete=models.CASCADE)
#     visit_date = models.DateField(auto_now_add=True)    #when the instance is created and auto_now is for whenever recore is updated
#     symptoms = models.TextField()
#     prescription = models.TextField()
#     amount_paid = models.PositiveIntegerField(default=0)
#     next_visit = models.DateField(null=True, blank=True)

#     def __str__(self):
#         return f"Paitent {self.patient.name} by Doctor {self.doctor.username}"