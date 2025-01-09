from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse, JsonResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# from django.core.validators import V
from django.core.mail import send_mail
from django.core.files.storage import default_storage
from django.utils.timezone import now
from .models import  User, Clinic, Patient, Prescription, Invoice
from random import randint

from .custom_token_generator import TokenGenerator
from cities_light.models import Country, Region, City 
from .serializers import RegionSerializers, CitySerializers





def login_in(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, "Invalid Credentional")
            return render(request, 'login.html')
               
        if user.is_password_reset:
            messages.error(request, "Please reset your password")
            return redirect('reset_password')

        login(request, user)

        if user.is_superuser:
            return redirect('home')
        
        if user.is_admin:
            return redirect('home')

        # if user.is_new_staff:
        #     return redirect('home')
         


@login_required(login_url='login')
def logout_user(request):
    logout(request)
    messages.success(request, "Logout successfully")
    return render(request, 'login.html')



def generate_otp():
    otp = randint(10000,99999)
    return otp


def forget_password(request):
    if request.method == 'GET':
        return render(request, 'forget_password.html')
    
    if request.method == 'POST':
        email = request.POST.get('email')

        if not email:
            messages.error(request, "Invalid email")
            return render(request, 'forget_password.html')
        if email:
            try:
                user = get_object_or_404(User, email=email)
            except Http404:
                messages.error(request, "Email is not registered")
                return render(request, 'forget_password.html')

            otp = generate_otp()
            send_mail('Your rest OTP', f'Your reset OTP is {otp}', 'noreply@gmail.com', [email,], fail_silently=False)
            return redirect('otp_verification', id=user.custom_id)
            #render(request, 'otp_verification.html')



def reset_password(request):
    if request.method == 'GET':
        return render(request, 'reset_password.html')

    if request.method == 'POST':
        email = request.POST.get('email')
        
        if not email:
            messages.error(request, "Invalid email")
            return render(request, 'reset_password.html')
        
        if email:
            try:
                user = get_object_or_404(User, email=email)
            except Http404:
                messages.error(request, "Email is not registered")
                return render(request, 'reset_password.html')

            otp = generate_otp()
            user.otp = otp
            user.save()
            user.custom_id
            send_mail('Password reset OTP', f'Your reset OTP is {otp}', 'noreply@gmail.com', [email,], fail_silently=False)

            return redirect('otp_verification', id=user.custom_id)  #render(request, 'otp_verification.html', {'id':user.custom_id})



def otp_verification(request, id):
    user = get_object_or_404(User, custom_id=id)
    
    if request.method == 'GET':
        return render(request, 'otp_verification.html', {'id':id})
    
    if request.method == 'POST':
        otp = request.POST.get('otp')
        
        if not otp or not otp.isdigit():
            messages.error(request, "please enter a valid OTP")
            return render(request, 'otp_verification.html', {'id':id})
        
        if otp != user.otp:
            messages.error(request, "please enter a valid OTP")
            return render(request, 'otp_verification.html', {'id':id})
        
        user.otp = None
        user.save()

        token = TokenGenerator().generate_token(user)
        return redirect('change_password', token=token)



def change_password(request, token):
    email = TokenGenerator().validate_token(token)
    if not email:
        messages.error(request, "Not a valid token")
        return redirect('reset_password')
    
    if request.method == 'POST':   
        user = get_object_or_404(User, email=email)        
        password = request.POST.get('password')

        if password and (len(password) >= 6 and len(password) <= 20):
            user.set_password(password)
            user.is_password_reset = False
            user.save()

            messages.success(request, 'Password reset successfully.')
            return redirect('login')
        
        messages.error(request, "Enter a valid password")

    return render(request, 'change_password.html', {'token':token})



@login_required(login_url='login')
def index(request):
    if request.method == 'GET':
        clinic = request.user.clinic.all().first()
        return render(request, 'index.html', {'clinic':clinic})



@login_required(login_url='login')
def all_users(request):
    if request.method == 'GET':
        if request.user.is_superuser:
            users = User.objects.exclude(email=request.user.email)
            return render(request, 'all_users.html', {'users':users})

        # if request.user.is_admin:
        #     clinics = User.objects.clinics.all()
        #     if clinics:
        #         user.objects.filter(Clinics__in=clinics)


@login_required(login_url='login')
def patients(request):
    if request.method == 'GET':
        if request.user.is_superuser:
            patients = Patient.objects.all()

        if request.user.is_admin:
            clinic = request.user.clinics.all().first()
            patients = Patient.objects.filter(clinic=clinic)
        
        return render(request, 'patients.html', {'patients':patients})
    


@login_required(login_url='login')
def profile(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        user = User.objects.get(username=request.user.username)
        user.first_name = first_name
        user.last_name = last_name

        if 'profile_img' in request.FILES:
            profile_img = request.FILES['profile_img']
            if user.profile_img:
                default_storage.delete(user.profile_img.path)
                
            user.profile_img = profile_img

        user.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('profile')

    return render(request, 'profile.html')



@login_required(login_url='login')
def clinic(request):
    if request.method == 'POST':
        name        = request.POST.get('name')
        state       = request.POST.get('state')
        city        = request.POST.get('city')
        pincode     = request.POST.get('pincode')
        address     = request.POST.get('address')
        email       = request.POST.get('email')
        number      = request.POST.get('number')
        specializations = request.POST.get('specializations')

        if state:
            state = get_object_or_404(Region, id=state)
        if city:
            city = get_object_or_404(City, region=state, id=city)

        clinic = Clinic.objects.filter(user=request.user).first()
        try:
            if clinic:
                clinic.name     = name
                clinic.state    = state
                clinic.city     = city
                clinic.pincode  = pincode
                clinic.address  = address
                clinic.email    = email
                clinic.number   = number
                clinic.specializations = specializations
                clinic.save()
            else:
                clinic = Clinic.objects.create(
                        user     = request.user,
                        name     = name,
                        state    = state,
                        city     = city,
                        pincode  = pincode,
                        address  = address,
                        email    = email,
                        number   = number,
                        specializations = specializations
                    )
            messages.success(request, 'Clinic details updated successfully.')
        except Exception as error:
            messages.error(request, 'Error with form data.')
        
        return redirect('home')



def country_states(request):
    state = Region.objects.filter(country=1).order_by('name')
    serializer = RegionSerializers(state, many=True)
    return JsonResponse({'region':serializer.data}, status=200)


def state_cities(request, region=None):
      if region:
            # state = Region.objects.filter(id=state).first()
            cities = City.objects.filter(region=region).order_by('name')#.only('id','name')
            serializer = CitySerializers(cities, many=True)
            return JsonResponse({'cities':serializer.data}, status=200)
      else:
          return JsonResponse({'cities':[]}, status=200)
          


@login_required(login_url='login')
def patients(request):
    if request.method == 'GET':
        if request.user.is_admin or request.user.is_superuser:
            clinic = Clinic.objects.filter(user=request.user).first()

            if not clinic:
                clinic      = Clinic.objects.none()
                patients    = Patient.objects.none()
            else:
                patients = Patient.objects.filter(clinic=clinic)

            context = {
                'clinic': clinic,
                'patients': patients,
            }
            return render(request, 'patitens_list.html', context)



@login_required(login_url='login')
def add_new_patient(request):
    if request.method == 'GET':
        return render(request, 'add_new_patient.html')
    
    if request.method == 'POST':
        if request.user.is_admin:
            doctor      = request.user
            clinic      = Clinic.objects.filter(user=doctor)
            name        = request.POST.get('name')
            age         = request.POST.get('age')
            gender      = request.POST.get('gender')
            number      = request.POST.get('number')
            address     = request.POST.get('address')
            medical_history = request.POST.get('medical_history')
        
            print(f"--------------{request.FILES.get('image')}-----------")
            try:
                patient = Patient.objects.create(
                        doctor   = doctor,
                        clinic   = clinic,
                        name     = name,
                        age      = age,
                        gender   = gender,
                        number   = number,
                        address  = address,
                        medical_history = medical_history
                    )
                
                if 'image' in request.FILES:
                    image = request.FILES['image']
                    patient.image = image
                    patient.save()
                    # if user.profile_img:
                    #     default_storage.delete(user.profile_img.path)
            except Exception as error:
                messages.error(request, "There is an error with form data.")

            return redirect('patients')

        # if request.user.is_superuser:
        #     pass 
# @login_required(login_url='login')
# def edit_profile(request):
#     if request.method == 'GET':
#         return render(request, '')
    
#     if request.method == 'POST':
#         return render(request, 'edit_profile.html')
    
        