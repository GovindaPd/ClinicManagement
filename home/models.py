from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.core.files.storage import default_storage


from cities_light.models import Region, City
from django.utils import timezone
from random import randint
from datetime import timedelta
import uuid
import random
import string
import os



indian_phone_regex = RegexValidator(
    regex=r'^(?:\+91|0)?[6-9]\d{9}$',
    message="Enter a valid Indian mobile number (e.g. +919812345678 or 09812345678 or 9812345678)."
)

def rename_image(instance, filename):
    extension = os.path.splitext(filename)[1]
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    new_name = f"{random_string}_{timezone.now().strftime('%d%m%Y%H%M%S')}{extension}"
    
    if isinstance(instance, User):
        return os.path.join('profile_img/', new_name)
    else:
        return os.path.join('reports/', new_name)


class CustomUserManager(UserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError('The username must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_password_reset', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if extra_fields.get('is_admin') is not True:
            raise ValueError('Superuser must have is_admin=True.')
        if extra_fields.get('is_password_reset') is not True:
            raise ValueError('Superuser must have is_password_reset=True.')

        return self.create_user(username, email, password, **extra_fields)
    
    # def get_queryset(self):
    #     return super().get_queryset().filter(is_active=True)


class User(AbstractUser):
    custom_id   = models.CharField(max_length=10, unique=True, blank=False, null=False)
    clinic      = models.ForeignKey('Clinic', on_delete=models.CASCADE, related_name="clinic_users", null=True, blank=True)
    profile_img = models.ImageField(upload_to=rename_image, blank=True)
    phone       = models.CharField(validators=[indian_phone_regex], max_length=15, blank=True, null=True)
    is_superuser= models.BooleanField(default=False)
    is_admin    = models.BooleanField(default=False)    # clinic admin
    is_admin_staff= models.BooleanField(default=False)    # clinic staff
    is_password_reset=models.BooleanField(default=False)
    is_active   = models.BooleanField(default=True)
    updated_at  = models.DateTimeField(auto_now=True)

    objects     = CustomUserManager()
    # USERNAME_FIELD = 'email'
    
    @property
    def user_type(self):
        if self.is_superuser:
            return "superuser"
        elif self.is_admin:
            return "admin"
        elif self.is_admin_staff:
            return "admin_staff"
        else:
            return "undefined"
        
    @staticmethod
    def generate_custom_id(max_attempts=10):
        for _ in range(max_attempts):
            custom_id = uuid.uuid4().hex[:10].upper()
            if not User.objects.filter(custom_id=custom_id).exists():
                return custom_id
        raise Exception("Unable to generate unique custom_id after multiple attempts.")
            
    def save(self, *args, **kwargs):
        if not self.custom_id:
            self.custom_id = self.generate_custom_id()
        super(User, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.username}"


class Clinic(models.Model):
    name    = models.CharField(max_length=255, help_text="Clinic Name", blank=False, null=False)
    address = models.CharField(max_length=255, blank=True)
    city    = models.ForeignKey(City, on_delete=models.SET_NULL, related_name="clinics_in_city", null=True, blank=True, max_length=255)
    state   = models.ForeignKey(Region, on_delete=models.SET_NULL, related_name="clinics_in_state", null=True, blank=True, max_length=255)
    pincode = models.CharField(max_length=6, null=True, blank=True)
    email   = models.EmailField(max_length=50, blank=True, null=True)
    number  = models.CharField(validators=[indian_phone_regex], max_length=15, blank=True, null=True)
    specializations = models.TextField(blank=True, null=True)   #clinic specilization

    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    class Meta:
        permissions = [
            ("can_approve_clinic", "Can Approve Clinic"),
            ("can_view_sensitive_data", "Can View Sensitive Data"),
        ]

    def __str__(self):
        return f"{self.name}"


class Patient(models.Model):
    BLOOD_GROUPS = (
        ('A+','A+'),
        ('A-','A-'),
        ('B+','B+'),
        ('B-','B-'),
        ('O+','O+'),
        ('O-','O-'),
        ('AB+','AB+'),
        ('AB-','AB-')  
    )
    doctor      = models.ForeignKey(User, related_name="patients", on_delete=models.CASCADE)
    clinic      = models.ForeignKey(Clinic, related_name='clinic_patients', on_delete=models.CASCADE)
    name        = models.CharField(max_length=255, null=False, blank=False)
    age         = models.FloatField(default=0, blank=True, null=True, validators=[MinValueValidator(0.0), MaxValueValidator(120.0)])
    gender      = models.CharField(max_length=10, choices=(("Male", "Male"), ("Female", "Female"), ("Other", "Other")), null=True, blank=True)
    number      = models.CharField(validators=[indian_phone_regex], max_length=15, blank=True, null=True, unique=False)
    address     = models.CharField(max_length=255, blank=True, null=True)
    medical_history = models.TextField(blank=True, default="")
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUPS, blank=True, null=True)
    image       = models.ImageField(upload_to=rename_image, blank=True) #report image or patient
    
    created_at  = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def delete(self, *args, **kwargs):
        if self.image:
            default_storage.delete(self.image.path)
        super().delete(*args, **kwargs)
    
    def __str__(self):
        return f"Patient Name: {self.name}, Clinin Name: {self.clinic.name}, Doctor Name: {self.doctor.username}"


class Prescription(models.Model):
    PAYMENT_STATUS = (
        ('Paid', 'Paid'),
        ('Pending', 'Pending'),
        ('Partial Paid', 'Partial Paid'),
    )
    patient     = models.ForeignKey(Patient, related_name="records", on_delete=models.CASCADE, null=False, blank=False)
    symptoms    = models.TextField(blank=True)
    prescription= models.TextField(blank=True)
    # dosage = models.CharField(max_length=50)
    image       = models.ImageField(upload_to=rename_image, blank=True)
    amount      = models.IntegerField(default=0)
    pending_amount= models.IntegerField(default=0)
    status      = models.CharField(max_length=15, choices=PAYMENT_STATUS, default='Paid')
    visit_date  = models.DateTimeField(auto_now_add=True)
    next_visit  = models.DateField(blank=True, null=True)

    # class Meta:
    #     permission = [
    #         ("can_clear_pending", "Can Clear Pending"),
    #     ]

    def delete(self, *args, **kwargs):
        if self.image:
            default_storage.delete(self.image.path)
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"Patient ID: {self.patient.id}, Patient Name: {self.patient.name}"


class Notification(models.Model):
    sender  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notes', null=False, blank=False)
    receiver= models.ManyToManyField(User, related_name='received_notes',)
    subject = models.CharField(max_length=250, blank=False, null=False)
    # message = models.TextField(blank=True, null=True)
    
    created_at= models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Message: {self.subject[:20]}..."


class SeenNotification(models.Model):
    note = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='seen_notes')
    seen_by = models.ForeignKey(User, on_delete=models.CASCADE)
    seen_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        unique_together = ('note', 'seen_by')  # prevent duplicates
    
    def __str__(self):
        return f"{self.seen_by.username} senn notification: {self.note.id}"


class BlockedIP(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)

    def __str__(self):
        return f"Blocked IP: {self.ip_address}"
    
# class RepetedAttempt(models.Model):
#     ip_address = models.GenericIPAddressField()
#     username = models.CharField(max_length=150, blank=True, null=True)
#     timestamp = models.DateTimeField(auto_now_add=True)

#     @classmethod
#     def too_many_attempts(cls, ip, limit=5, minutes=5):
#         """
#         Returns True if the IP has exceeded `limit` attempts within `minutes`.
#         """
#         cutoff = timezone.now() - timedelta(minutes=minutes)
#         recent = cls.objects.filter(ip_address=ip, timestamp__gte=cutoff).count()
#         return recent >= limit
