from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse, JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import update_last_login
from django.contrib import messages
# from django.core.validators import V
from django.core.mail import send_mail
from django.core.files.storage import default_storage
from django.utils.timezone import now
from django.conf import settings
from django.urls import resolve
from urllib.parse import urlparse
from django.utils.timezone import now
from django.db import transaction
from django.db import OperationalError, IntegrityError
from django.core.exceptions import ValidationError
from cities_light.models import Country, Region, City 
from random import randint


from .models import  User, Clinic, Patient, Prescription, Invoice
from .custom_token_generator import TokenGenerator
from .serializers import RegionSerializers, CitySerializers

import os



def generate_otp():
    otp = randint(10000,99999)
    return otp

def get_url_name(full_url):
    """ return url name """
    if full_url:
        parsed_url = urlparse(full_url)
        path = parsed_url.path
        try:
            url_match = resolve(path)
            return url_match.url_name
        except Exception:
            return None
    else:
        return None

# referer = request.META.get('HTTP_REFERER')
# url_name = get_url_name(referer)


def login_in(request):
    if request.method == 'GET':
        return render(request, 'login.html', {"login_page": True})
    
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, "Invalid Credentionals!")
            return render(request, 'login.html', {"login_page": True})
               
        if user.is_superuser:
            login(request, user)
            update_last_login(None, user)  # Ensure last login is updated
            return redirect('/admin/')
        
        elif user.is_admin:
            if user.is_password_reset:
                messages.info(request, "We had send a password reset link to your email.")
                token = TokenGenerator().generate_token(user)
                reset_url = request.build_absolute_uri(f'/reset-password/{token}/')
                
                send_mail(
                    subject="Password Reset Request",
                    message=f"Click the link below to reset your password:\n\n{reset_url}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                )
                return redirect('login')

            login(request, user)
            if remember_me:
                request.session.set_expiry(3600 * 24 * 30) # 7 days in seconds

            return redirect('home')


@login_required(login_url='login')
def logout_user(request):
    logout(request)
    messages.success(request, "Logout successfully!")
    return redirect('login')


def reset_password(request, token):
    email = TokenGenerator().validate_token(token)
    if not email:
        messages.error(request, "Not a valid token")
        return redirect('login')
    
    if request.method == 'GET':
        return render(request, 'reset_password.html', {'token':token})
    
    if request.method == 'POST':
        user = get_object_or_404(User, email=email)
        password = request.POST.get('password')

        if password and (len(password) >= 6 and len(password) <= 20):
            user.set_password(password)
            user.is_password_reset = False
            user.save()

            messages.success(request, 'Password update successfully.')
            return redirect('login')
        
        messages.error(request, "Enter a valid password")
        return render(request, 'reset_password.html', {'token':token})


def forget_password(request):  
    # if request.method == 'GET':
    #     return render(request, 'forget_password.html')

    if request.method == 'POST':
        email = request.POST.get('email')
        
        if not email:
            messages.error(request, "Invalid email!")
            return render(request, 'forget_password.html')
        
        if email:
            try:
                user = get_object_or_404(User, email=email)
            except Http404:
                messages.error(request, "Email is not registered!")
                return render(request, 'login.html', {'login_page': False})

            otp = generate_otp()
            user.otp = otp
            user.save()
            user.custom_id

            send_mail('Password forget request OTP', f'Your forget password OTP is {otp}', 'noreply@gmail.com', [email,], fail_silently=False)
            return render(request, 'otp_verification.html', {'id':user.custom_id})
            #return redirect('otp_verification', id=user.custom_id)
  

def otp_verification(request, id):
    if request.method == 'POST':
        user = get_object_or_404(User, custom_id=id)
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
        request.session['token'] = token

        return render(request, 'change_password.html')
        

def change_password(request):
    if request.method == 'POST':
        if token:= request.session.get('token'):
            email = TokenGenerator().validate_token(token)

            if not email:
                messages.error(request, "Not a valid token")
                return redirect('forget_password')

            user = get_object_or_404(User, email=email)        
            password = request.POST.get('password')

            if password and (len(password) >= 6 and len(password) <= 20):
                user.set_password(password)
                user.save()

                del request.session['token']
                messages.success(request, 'Password update successfully.')
                return redirect('login')
            
            messages.error(request, "Enter a valid password")
            return render(request, 'change_password.html')
        
        else:
            return redirect('login')


@login_required(login_url='login')
def change_user_password(request):
    if request.method == 'GET':
        return render(request, 'change_user_password.html')
    
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        password     = request.POST.get('password')

        user = get_object_or_404(User, username=request.user.username)
        if user.check_password(old_password):
            if password and (len(password) >= 6 and len(password) <= 20):
                user.set_password(password)
                user.save()
                messages.success(request, 'Password update successfully.')
            else:
                messages.warning(request, "Password not changed. Please enter valid new password.")
        else:
            messages.error(request, "Password does not match.")
        return redirect('change_user_password')



@login_required(login_url='login')
def index(request):
    if request.method == 'GET':
        return render(request, 'index.html')



@login_required(login_url='login')
def all_users(request):
    if request.method == 'GET':
        if request.user.is_superuser:
            users = User.objects.exclude(username=request.user.username)
        elif request.user.is_admin:
            clinic = request.user.clinic
            if clinic:
                users = User.objects.filter(clinic=clinic)
            else:
                users = None
        return render(request, 'user_list.html', {'users':users})
    
    return HttpResponseBadRequest()


@login_required(login_url='login')
def check_unique(request):
    if request.method == 'GET':
        field = request.GET.get('field')
        value = request.GET.get('value')
        if field == 'email':
            exists = User.objects.filter(email=value).exists()
            
        elif field == 'username':
            exists = User.objects.filter(username=value).exists()
        else:
            exists = None

        if exists != None:
            message = f"{field} is not available" if exists == True else f"{field} is available"
        else:
            message = None
        return JsonResponse({'exists':exists, 'message':message})
    return HttpResponseBadRequest()



@login_required(login_url='login')
def add_user(request):
    if not any([request.user.is_superuser, request.user.is_admin]):
        return HttpResponseForbidden(f"{request.user.is_superuser=} or {request.user.is_admin=}:")
    
    if request.method == 'GET':
        if request.user.is_superuser:
            clinics = Clinic.objects.all().values_list('id','name')
        elif request.user.is_admin:
            if not request.user.clinic:
                messages.error(request, "You have not fill your clinic details yet.")
                return redirect('all_users')
            clinics = Clinic.objects.filter(id = request.user.clinic.id).values_list('id','name')
        return render(request, 'add_user.html', {'clinics':clinics})
    
    elif request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name','')
        last_name = request.POST.get('last_name','')
        user_type = request.POST.get('user_type','')
        clinic = request.POST.get('clinic', None)
        
        if clinic:
            xyz = Clinic.objects.filter(id=clinic)
            if xyz.exists():
                clinic = xyz.first()
                clinic_exists = True
        else:
            clinic = None
            clinic_exists = False

        if request.user.is_superuser:
            if user_type == 'admin':
                is_admin = True
                is_new_staff = False
            elif user_type == 'is_new_staff':
                is_admin = False
                is_new_staff = True
                
                if not clinic and not clinic_exists:
                    messages.error(request, "You do not have selected any clinic.")
                    return redirect('all_users')
            else:
                messages.error("user type is not defined")
                return redirect('all_users')
        else:
            is_admin = False
            is_new_staff = True
            if not clinic and not clinic_exists:
                messages.error(request, "You do not have selected any clinic.") 
                return redirect('all_users')

        try:
            user = User.objects.create(
                username    = username,
                email       = email,
                first_name  = first_name,
                last_name   = last_name,
                is_admin    = is_admin,
                is_new_staff = is_new_staff,
                clinic       = clinic
            )
            default_password = "temp1234"
            user.set_password(default_password)
            user.save()
            
            from_user   = request.user.username,
            to          = username,
           
            # if user.is_admin:
            #      message = f"""Dear {username}
            # Congratulations! Your account, has been successfully added to our system. 🚀Now you can start managing patient records, appointments, and more—all in one place!
            # 📌Need help getting started? Check out our [Help Center] or reach out to our support team anytime.
            # Thank you for trusting {settings.WEBSITE_NAME} to streamline your clinic management! 💙"""
            # elif user.is_new_staff:
            #     message = f"Welcome to {clinic.name}! We’re excited to have you on board and look forward to the amazing impact you’ll bring to our team and patients. 
            #     Wishing you success in this new journey! ✨"
            # noti = Notifications.objects.create(
            #         from_user = from_user,
            #         to        = to,
            #         message   = message                             
            # )
            messages.success(request, f"New account has been created successfully {username=} and {default_password=}")

            send_mail(
                subject = f"New accounted on created on {settings.WEBSITE_NAME}",
                message = f"your username is {username} and temporary password is {default_password}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email,],
                fail_silently=False
            )
            
        except IntegrityError as e:
             messages.error(request, "Error within form data.")
        except ValidationError as ve:
            messages.error(request, "Error within form data validation.")
        except OperationalError:
            messages.error(request, "Database server being down or unreachable.")
        except ValueError:
            messages.error(request, "Value error.")
        
        return redirect('all_users')
    return HttpResponseBadRequest()



@login_required(login_url='login')
def edit_user(request):
    if not any([request.user.is_superuser, request.user.is_admin]):
        return HttpResponseForbidden(f"{request.user.is_superuser=} or {request.user.is_admin=}")
# if clinics:
#     user.objects.filter(Clinics__in=clinics)

@login_required(login_url='login')
def update_user_status(request):
    if request.method == 'POST':
        custom_id = request.POST.get('user_id')
        try:
            status    = int(request.POST.get('status',''))
        except ValueError:
            return HttpResponseBadRequest()
        active,msg = (True, "{} account activated successfully.") if status else (False, "{} account deactivated successfully.")

        if request.user.is_superuser:
            users = User.objects.filter(custom_id=custom_id)
            if users.exists():
                user = users.last()
                user.is_active = active
                user.save()
                messages.info(request, msg.format(user.username))
            else:
                messages.error(request, "There is no user with given id.")
            
        elif request.user.is_admin:
            if request.user.clininc:
                users = User.objects.filter(custom_id=custom_id, clinic=request.user.clininc)
                if users.exists():
                    user = users.last()
                    user.is_active = active
                    user.save()
                    messages.info(request, msg.format(user.username))
                else:
                     messages.error(request, "There is no user with given id.") 
            else:
                messages.error(request, "You do not have fill clinic details yet.") 
        else:
            return HttpResponseForbidden()
        return redirect('all_users')
    return HttpResponseBadRequest()          



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
        if not request.user.is_admin:
            return HttpResponseForbidden()
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
                patients = Patient.objects.filter(clinic=clinic).order_by('-created_at')

            context = {
                'clinic': clinic,
                'patients': patients,
            }
            return render(request, 'patitens_list.html', context)
    return HttpResponseBadRequest()


@login_required(login_url='login')
def add_new_patient(request):
    if request.user.is_admin:
        if request.method == 'GET':
            if not request.user.clinic:
                messages.error(request, "You have not fill your clinic details yet.")
                return redirect('patients')
            return render(request, 'add_new_patient.html')
        
        if request.method == 'POST':
            doctor      = request.user
            clinic      = Clinic.objects.filter(user=doctor).first()
            
            if not clinic:
                messages.error(request, "You are not joined to any clinic.")
                return redirect('patients')
            
            name        = request.POST.get('name')
            age         = request.POST.get('age') or None
            gender      = request.POST.get('gender')
            number      = request.POST.get('number')
            address     = request.POST.get('address')
            medical_history = request.POST.get('medical_history')
            blood_group = request.POST.get('blood_group')
        
            try:
                patient = Patient.objects.create(
                        doctor          = doctor,
                        clinic          = clinic,
                        name            = name,
                        age             = age,
                        gender          = gender,
                        number          = number,
                        address         = address,
                        medical_history = medical_history,
                        blood_group     = blood_group
                    )
                
                if 'image' in request.FILES:
                    image = request.FILES['image']
                    patient.image = image
                    patient.save()
                    # if user.profile_img:
                    #     default_storage.delete(user.profile_img.path)
                messages.success(request, "Patient details added successfully.")
            except Exception as error:
                messages.error(request, "There is an error with form data.")

            return redirect('patients')
    else:
        return HttpResponseForbidden()
        

@login_required(login_url='login')
def edit_patient(request, patient_id):
    if request.method == 'GET':
        clinic = request.user.clinic
        doctor = request.user
    
        if request.user.is_admin:
            patient = get_object_or_404(Patient, id=patient_id, clinic=clinic)  #patinet of perticuler doctor
        # elif request.user.is_new_staff:
        #     patient = get_object_or_404(Patient, id=patient_id, clinic=clinic, doctor=doctor)
        return render(request, 'edit_patient.html', {'patient':patient})

    if request.method == 'POST':
        name        = request.POST.get('name')
        age         = request.POST.get('age')
        gender      = request.POST.get('gender')
        number      = request.POST.get('number')
        address     = request.POST.get('address')
        medical_history = request.POST.get('medical_history')
        blood_group = request.POST.get('blood_group')
        image       = request.FILES.get('image')

        if request.user.is_admin:
            doctor = request.user
            clinic = request.user.clinic
        
        patient = get_object_or_404(Patient, id=patient_id, clinic=clinic, doctor=doctor)
        try:
            patient.name        = name
            patient.age         = age
            patient.gender      = gender
            patient.number      = number
            patient.address     = address
            patient.medical_history = medical_history
            patient.blood_group = blood_group

            if image:
                if patient.image:
                    default_storage.delete(patient.image.path)
                    patient.image = image
            patient.save()
            messages.success(request, "Patient details updates successfully.")
        except Exception as error:
            messages.error(request, "There is an error with form data.")

        return redirect('patients')


@login_required(login_url='login')
def delete_patient(request, patient_id):
    if request.method == 'GET':
        clinic = request.user.clinic
        doctor = request.user
        
        if request.user.is_admin:
            patient = get_object_or_404(Patient, id=patient_id, clinic=clinic)  #patinet of perticuler doctor
        # elif request.user.is_new_staff:
        #     patient = get_object_or_404(Patient, id=patient_id, clinic=clinic, doctor=doctor)

        patient.delete()
        messages.success(request, "Patient deleted successfully.")
        return redirect ('patients')
    
    return HttpResponseBadRequest()


@login_required(login_url='login')
def patient_details(request, patient_id):
    if request.method == 'GET':
        patient = Patient.objects.filter(id=patient_id).first()
        if patient:
            prescriptions = Prescription.objects.filter(patient=patient).order_by('visit_date')
            context = {
                'patient' : patient,
                'prescriptions' : prescriptions,
            }
        else: 
            context = {
                'patient' : Patient.objects.none(),
                'prescriptions' : Prescription.objects.none(),
            }
        
        return render(request, 'patient_details.html', context)



@login_required(login_url='login')
def add_patient_visit(request, patient_id):
    today = now().date()
    today = today.strftime("%Y-%m-%d")

    if request.method == 'GET':
        return render(request, 'add_patient_visit.html', {'today': today})
    
    if request.method == 'POST':
        patient = get_object_or_404(Patient, id=patient_id)

        symptoms = request.POST.get('symptoms')
        prescription = request.POST.get('prescription')
        visit_date = request.POST.get('visit_date',)
        next_visit = request.POST.get('next_visit') or None
        image = request.FILES.get('image')
        amount = request.POST.get('amount',0)
        paid_amount = request.POST.get('paid_amount',0)
        
        try:
            amount = int(amount)
            paid_amount = int(paid_amount)
            pending_amount = amount - paid_amount
        except ValueError:
            messages.error(request, "amount value is not integer")
            return render(request, 'add_patient_visit.html', {'today': today})
        
        if amount == paid_amount:
            status = 'Paid'
        elif paid_amount == 0 and amount !=0:
            status = 'Pending'
        else:
            status = 'Partial Paid'
       
        try:
            with transaction.atomic():
                prescription = Prescription.objects.create(
                    patient         = patient,
                    symptoms        = symptoms,
                    prescription    = prescription,
                    visit_date      = visit_date,
                    next_visit      = next_visit
                )
                if image:    
                    prescription.image = image
                    prescription.save()
                
                invoice = Invoice.objects.create(
                    prescription = prescription,
                    amount = amount,
                    pending_amount = pending_amount,
                    status = status
                )
        except Exception as e:
            messages.error(request, f"Error occurred: {str(e)}")
        else:
            messages.success(request, "new visit added successfully.")

        return redirect('patient_details', patient_id=patient_id)

    

@login_required(login_url='login')
def edit_patient_visit(request, patient_id, visit_id):
    if request.method == 'GET':
        prs = Prescription.objects.filter(id=visit_id).first()
        return render(request, 'edit_patient_visit.html', {'today': now().date(), 'prs':prs, 'patient_id':patient_id, 'visit_id':visit_id})
    
    if request.method == 'POST':
        doctor = request.user
        #clinic = Clinic.objects.get(user=doctor)
        
        if request.user.is_admin:
            clinic = request.user.clinic
        # elif request.user.is_new_staff:
        #     pass

        patient = get_object_or_404(Patient, id=patient_id, doctor=doctor)  #patinet of perticuler doctor
        prs = get_object_or_404(Prescription, id=visit_id, patient=patient) #prescription of perticuler 

        symptoms = request.POST.get('symptoms')
        prescription = request.POST.get('prescription')
        visit_date = request.POST.get('visit_date')
        next_visit = request.POST.get('next_visit')
        image = request.FILES.get('image')
        amount = request.POST.get('amount',0)
        paid_amount = request.POST.get('paid_amount',0)
        
        try:
            amount = int(amount)
            paid_amount = int(paid_amount)
            pending_amount = amount - paid_amount
        except ValueError:
            messages.error("amount value is not integer")
            return redirect('patient_details', patient_id=patient_id)
        
        if amount == paid_amount:
            status = 'Paid'
        elif paid_amount == 0 and amount !=0:
            status = 'Pending'
        else:
            status = 'Partial Paid'
       
        try:
            with transaction.atomic():
                prs.symptoms        = symptoms
                prs.prescription    = prescription
                prs.visit_date      = visit_date
                prs.next_visit      = next_visit
                
                if image:
                    if prs.image:
                        os.remove(prs.image.path)
                    prs.image = image

                prs.invoice.amount = amount
                prs.invoice.pending_amount = pending_amount
                prs.invoice.status = status

                prs.save()

        except Exception as e:
            messages.error(request, f"Error occurred: {str(e)}")
        else:
            messages.success(request, "Visit updated successfully.")

        return redirect('patient_details', patient_id=patient_id)
    


@login_required(login_url='login')
def delete_patient_visit(request, patient_id, visit_id):
    if request.method == 'GET':
        clinic = request.user.clinic
        doctor = request.user
        
        if request.user.is_admin:
            patient = get_object_or_404(Patient, id=patient_id, clinic=clinic)  #patinet of perticuler doctor
        # elif request.user.is_new_staff:
        #     patient = get_object_or_404(Patient, id=patient_id, clinic=clinic, doctor=doctor)

        prs = get_object_or_404(Prescription, id=visit_id, patient=patient) #perticuler prescription of patient 
        prs.delete()

        messages.success(request, "Visit deleted successfully.")
        return redirect ('patient_details', patient_id=patient_id)
    
    return HttpResponseBadRequest()



# ROUGHT
@login_required(login_url='login')
def rough(request):
    if request.method == 'GET':
        return render(request, 'hekathon.html')#'chess.html'