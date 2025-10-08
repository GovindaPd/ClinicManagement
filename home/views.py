from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import update_last_login
from django.contrib.auth.decorators import permission_required
from django.views.decorators.http import require_http_methods

from django.core.mail import send_mail
from django.urls import resolve, reverse
from django.utils.timezone import now

from django.conf import settings
from django.core.files.storage import default_storage

from django.contrib import messages
from django.db import transaction
from django.db import OperationalError, IntegrityError
from django.db.models import Count, Exists, OuterRef, F, Q, Sum
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group, Permission
from django.http import Http404, HttpResponse, JsonResponse, HttpResponseForbidden, HttpResponseBadRequest

from cities_light.models import Country, Region, City

from .models import  User, Clinic, Patient, Prescription, Notification, SeenNotification
from .custom_token_generator import TokenGenerator
from .serializers import RegionSerializers, CitySerializers
from .secret_variables import *

import os
import json
import string
from random import randint, choices
from urllib.parse import urlparse
from collections import defaultdict

# referer = request.META.get('HTTP_REFERER')
# url_name = get_url_name(referer)

forbidden_message = """You do not have permission to access this resource.
    Please check that you have the correct credentials or contact the site administrator if you believe this is an error."""

def generate_otp():
    otp = randint(100000,999999)
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

def generate_password(length = 8):
    """ generate password """
    return ''.join(choices(string.ascii_letters+string.digits, k=length))


def send_welcome_mail(request, user, clinic=None, default_password=None):
    if request.user.is_superuser:
        if user.is_admin:
            subject = admin_welcome_subject
            message = admin_welcome_mail.format(user.username, company_name, company_name)
        elif user.is_admin_staff:
            subject = admin_staff_welcome_subject.format(clinic.name)
            message = admin_staff_welcome_mail.format(user.username, clinic.name, clinic.name)
        else:
            subject = all_welcome_subject.format(company_name)
            message = all_welcome_message.format(user.username)

    elif request.user.is_admin:
        subject = admin_staff_welcome_subject.format(clinic.name)
        message = admin_staff_welcome_mail.format(user.username, clinic.name, clinic.name)
        
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email], 
        fail_silently=True
    )
    

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


# -------------- views start here -----------------
@require_http_methods(["GET", "POST"])
def login_in(request):
    """ login user """
    if request.method == 'GET':
        return render(request, 'login.html')
    
    elif request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, "Invalid Credentionals!")
            return render(request, 'login.html')
        
        # if user.is_password_reset:
            #     messages.info(request, "We have send a password reset link to your email.")
            #     token = TokenGenerator().generate_token(user)
            #     reset_url = request.build_absolute_uri(f'/reset-password/{token}/')
                
            #     send_mail(
            #         subject="Password Reset Request",
            #         message=f"Click the link below to reset your password:\n\n{reset_url}",
            #         from_email=settings.DEFAULT_FROM_EMAIL,
            #         recipient_list=[user.email],
            #     )
            #     return redirect('login')
               
        login(request, user)
        update_last_login(None, user)

        if remember_me:
            request.session.set_expiry(3600 * 24 * 30)  #30 days in seconds

        if user.is_superuser:
            # return redirect('/admin/')
            pass
        elif user.is_admin:
            pass
        
        return redirect('home')


@require_http_methods(["GET"])
@login_required(login_url='login')
def index(request):
    """dashboard view """
    if request.method == 'GET':
        if request.user.is_superuser:
            total_clinics = Clinic.objects.count()
            total_staffs  = User.objects.count()
            total_patients= Patient.objects.count()
            # recent_patients = Patient.objects.all().order_by('-created_at')[:5]
            context = {
                'total_clinics': total_clinics,
                'total_staffs' : total_staffs,
                'total_patients': total_patients,
                'load_chart_js': True
                # 'total_doctors': total_doctors,
                # 'recent_patients': recent_patients,
            }
        elif request.user.is_admin:
            total_staffs= User.objects.filter(clinic=request.user.clinic_id).count()
            patients = Patient.objects.filter(clinic=request.user.clinic_id).prefetch_related('records')
            total_patients = patients.count()
            total_pending_payments = 0
            patient_data = []
            
            age_wise_patients = {"Child":0, "Teen":0, "Adult":0, "Senior":0, "Unknown":0, }
            gender_wise_patients = {"Male":0, "Female":0, "Other":0, "Unknown":0}
            monthlyIncomeGrouped = defaultdict(lambda: defaultdict(int))
            monthlyPatientGrouped = defaultdict(lambda: defaultdict(int))

            for patient in patients:
                if patient.gender:
                    gender_wise_patients[patient.gender.capitalize()] += 1
                else:
                    gender_wise_patients["Unknown"] += 1
                
                if patient.age:
                    age_type = "Child" if patient.age<13 else "Teen" if patient.age<18 else "Adult" if patient.age<60 else "Senior"
                    age_wise_patients[age_type] += 1
                else:
                    age_wise_patients['Unknown'] += 1

                for prescription in patient.records.all():
                    if prescription.status in ['Pending', 'Partial Paid']:
                        total_pending_payments += 1
                    
                    if prescription.visit_date:
                        monthlyIncomeGrouped[prescription.visit_date.year][prescription.visit_date.month] += prescription.amount
                        monthlyPatientGrouped[prescription.visit_date.year][prescription.visit_date.month] += 1

            monthWiselabels = []
            monthWiseIncomes = []
            monthWisePatients = []
            min_year = min(monthlyIncomeGrouped.keys())
            max_year = max(monthlyIncomeGrouped.keys())
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print(monthlyIncomeGrouped[min_year].keys())
            monthName = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}


            for year in range(min_year, max_year + 1):
                for month in range(1, 13):
                    if year == min_year and month not in monthlyIncomeGrouped[min_year].keys(): # don't get any date before clinic open
                        continue
                    if year > now().year or (year == now().year and month > now().month):   # don't get any future date data
                        break
                    monthWiselabels.append(f"{monthName[month]}-{year}")
                    monthWiseIncomes.append(monthlyIncomeGrouped[year][month])
                    monthWisePatients.append(monthlyPatientGrouped[year][month])
                    
            context = {
                'total_staffs' : total_staffs,
                'total_patients': total_patients,
                'total_pending_payments': total_pending_payments,
                'age_wise_patients': age_wise_patients,
                
                'gender_keys':json.dumps(list(gender_wise_patients.keys())),
                'gender_values':json.dumps(list(gender_wise_patients.values())),
                
                "age_wise_keys": json.dumps(list(age_wise_patients.keys())),
                "age_wise_values": json.dumps(list(age_wise_patients.values())),

                # year wise earning data
                "monthWiselabels": json.dumps(monthWiselabels),
                "monthWiseIncomes": json.dumps(monthWiseIncomes),
                "monthWisePatients": json.dumps(monthWisePatients),
                'load_chart_js': True
            }
        else:
            context = {
                'load_chart_js': True
            }
        return render(request, 'index.html', context)
    

@require_http_methods(["GET"])
@login_required(login_url='login')
def logout_user(request):
    """ logout user """
    logout(request)
    messages.success(request, "Logout successfully!")
    return redirect('login')


@require_http_methods(['GET', 'POST'])
def password_reset(request):
    if request.method == 'GET':
        return render(request, 'password_reset.html')
    
    elif request.method == 'POST':
        email = request.POST.get('email')
        if not email:
            messages.error(request, "Invalid email!")
            return render(request, 'password_reset.html')
    
        try:
            user = get_object_or_404(User, email=email)
        except Http404:
            messages.error(request, "Email is not registered!")
            return render(request, 'password_reset.html')
        
        token = TokenGenerator.generate_token(user)
        uuid = TokenGenerator.encode_string(user.custom_id)
        send_mail(
            forget_password_header, 
            forget_password_body.format(
                user.username, 
                request.build_absolute_uri(reverse('password_reset_confirm', kwargs={'uid64':uuid, 'token':token})), 
                company_name),
            settings.DEFAULT_FROM_EMAIL, 
            [email], 
            fail_silently=True
        )
        return redirect('password_reset_done')


@require_http_methods(["GET"]) 
def password_reset_done(request):
    return render(request, "password_reset_done.html")


@require_http_methods(["GET", "POST"])
def password_reset_confirm(request, uid64, token):
    user_id = TokenGenerator.decode_string(uid64)
    user = get_object_or_404(User, custom_id=user_id)

    validated_token = TokenGenerator.validate_token(token)
    if validated_token:
        if TokenGenerator.compare_token(user, validated_token):
            if request.method == "POST":
                password = request.POST.get("password")
                if password and len(password) >= 8 and len(password) <= 30:
                    user.set_password(password)
                    user.save()
                    messages.success(request, "Password changed successfully")
                    return redirect("login")
                messages.error(request, "Invalid Password")
            return render(request, "password_reset_confirm.html")

    messages.error(request, "Link has been expired")
    return redirect('password_reset')


@require_http_methods(["GET", "POST"])
@login_required(login_url='login')
def change_user_password(request):
    if request.method == 'GET':
        return render(request, 'change_user_password.html')
    
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        password     = request.POST.get('password')

        user = get_object_or_404(User, username=request.user.username)
        if user.check_password(old_password):
            if password and (len(password) >= 8 and len(password) <= 30):
                user.set_password(password)
                user.save()
                messages.success(request, 'Password updated successfully.')
            else:
                messages.warning(request, "Password not changed. Please enter valid new password.")
        else:
            messages.error(request, "Old Password does not match.")
        return redirect('change_user_password')


@require_http_methods(["GET"])
@login_required(login_url='login')
@permission_required(['home.view_user'], raise_exception=True)
def all_users(request):
    users = User.objects.none()
    if request.user.is_superuser:
        users = User.objects.exclude(username=request.user.username)
    elif request.user.is_admin:
        clinic = request.user.clinic
        if clinic:
            users = User.objects.filter(clinic=clinic).exclude(username=request.user.username)
    else:
        return HttpResponseForbidden(forbidden_message)
    return render(request, 'user_list.html', {'users':users})


@require_http_methods(["GET", "POST"])
@login_required(login_url='login')
@permission_required(['home.add_user'], raise_exception=True)
def add_user(request):    
    if request.method == 'GET':
        clinics = Clinic.objects.none()
        if request.user.is_superuser:
            clinics = Clinic.objects.all().values_list('id','name')
        elif request.user.is_admin:
            if not request.user.clinic:
                messages.error(request, "You do not have registerd clinic details")
                return redirect('all_users')
            clinics = Clinic.objects.filter(id = request.user.clinic_id).values_list('id','name')
        return render(request, 'add_user.html', {'clinics':clinics, 'search_bar':"flase"})
    
    if request.method == 'POST':
        is_admin = False
        is_admin_staff = False
        default_password = generate_password(length=12)
        clinic = None
        clinic_exists = False
        user_group = Group.objects.none()

        email = request.POST.get('email')
        username = request.POST.get('username')
        first_name = request.POST.get('first_name','')
        last_name = request.POST.get('last_name','')
        user_type = request.POST.get('user_type','')
        user_clinic = request.POST.get('clinic', None)
        
        if user_clinic:
            try:
                user_clinic = int(user_clinic)
            except (ValueError, TypeError):
                messages.error("user clinic id is not integer")

            cl = Clinic.objects.filter(id=user_clinic)
            if cl.exists():
                clinic = cl.first()
                clinic_exists = True
        
        if request.user.is_superuser:
            if user_type == 'is_admin':
                is_admin = True
                user_group = Group.objects.filter(name="clinic_admin")
            elif user_type == 'is_admin_staff':
                is_admin_staff = True
                user_group = Group.objects.filter(name="clinic_staff")
                if not clinic_exists:
                    messages.error(request, "You do not have selected any clinic.")
                    return redirect('all_users')
        elif request.user.is_admin:
            is_admin_staff = True
            user_group = Group.objects.filter(name="clinic_staff")
            if not clinic_exists:
                messages.error(request, "You do not have selected any clinic.") 
                return redirect('all_users')
        else:
            messages.error(request, "You do not have permission to add staff.")
            return redirect('all_users')

        try:
            user = User.objects.create_user(
                username    = username,
                email       = email,
                first_name  = first_name,
                last_name   = last_name,
                clinic      = clinic,
                password    = default_password,
                is_admin    = is_admin,
                is_admin_staff= is_admin_staff
            )
            if user_group.exists():
                user.groups.set(user_group)
                user.save()
        except IntegrityError:
            messages.error(request, "Error with form data insertion.")
            return redirect('add_user')
        except ValidationError:
            messages.error(request, "Error with form data validation.")
            return redirect('add_user')
        except OperationalError:
            messages.error(request, "Database server being down or unreachable. Please try again later.")
            return redirect('add_user')
        except ValueError:
            messages.error(request, "Form values are required.")
            return redirect('add_user')

        send_welcome_mail(request, user, clinic)
        messages.success(request, f"{user.username} account has been created successfully. Default password is {default_password!r}")
        return redirect('all_users')
  

@require_http_methods(["GET", "POST"])
@login_required(login_url='login')
@permission_required(['home.change_user', 'home.view_user'])
def edit_user(request, user_id):
    user = User.objects.none()
    clinics = Clinic.objects.none()
    clinic_exists = False

    try:
        if request.user.is_superuser:
            user = User.objects.prefetch_related('groups').get(custom_id=user_id)
            clinics = Clinic.objects.all().values_list('id','name')
        elif request.user.is_admin:
            if not request.user.clinic:
                messages.error(request, "You do not have registerd clinic details.")
                return redirect('all_users')
            else:
                user = User.objects.prefetch_related('groups').get(custom_id=user_id, clinic=request.user.clinic_id)
                clinics = Clinic.objects.filter(id = request.user.clinic_id).values_list('id','name')
        else:
            return HttpResponseForbidden(forbidden_message)
    except (User.DoesNotExist, User.MultipleObjectsReturned):
        messages.error(request, "User not exist with given id.")
        return redirect('all_users')
    
    if request.method == "GET":
        groups = Group.objects.exclude(id__in=user.groups.values_list('id', flat=True))
        return render(request, 'edit_user.html', {'user':user, 'clinics':clinics, 'groups':groups, 'search_bar':"flase"})
    
    if request.method == 'POST':            
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name','')
        last_name = request.POST.get('last_name','')
        user_type = request.POST.get('user_type','')
        user_clinic = request.POST.get('clinic', None)
        user_grp = request.POST.getlist('choosen_groups', [])
        user_group = []

        if user_clinic:
            try:
                user_clinic = int(user_clinic)
            except (ValueError, TypeError):
                messages.error(request, "clinic id must be an integer.")
            
            cl = Clinic.objects.filter(id=user_clinic)
            if cl.exists():
                clinic = cl.first()
                clinic_exists = True

        if request.user.is_superuser:
            for gp in user_grp:
                try:
                    gp =int(gp)
                    user_group.append(gp)
                except (TypeError, ValueError):
                    pass
            grp_objs = Group.objects.filter(id__in=user_group) if user_group else []
            if grp_objs:
                user.groups.set(grp_objs)
            else:
                user.groups.clear()

            if user_type == 'is_admin':
                user.is_admin = True
                user.is_admin_staff = False
                if clinic_exists:
                    user.clinic = clinic
            elif user_type == 'is_admin_staff':
                user.is_admin = False
                user.is_admin_staff = True
                if clinic_exists:
                    user.clinic = clinic
                # else:
                #     messages.error(request, "You do not have selected any clinic.")
                #     return redirect('all_users')
        elif request.user.is_admin:
            user.is_admin_staff = True
            if clinic_exists and request.user.clinic==clinic:
                user.clinic = clinic
            else:
                messages.error(request, "You do not have selected any clinic.") 
                return redirect('all_users')
        else:
            messages.error(request, "You do not have permission to add staff.")
            return redirect('all_users')
        
        user.username = username if username else user.username
        user.email = email if email else user.email
        user.first_name = first_name if first_name else user.first_name
        user.last_name = last_name if last_name else user.last_name
        
        try:
            user.save()
        except IntegrityError as e:
            messages.error(request, "Error with form data insertion.")
            return redirect('edit_user', user_id=user_id)
        except ValidationError as ve:
            messages.error(request, "Error with form data validation.")
            return redirect('add_user')
        except OperationalError:
            messages.error(request, "Database server being down or unreachable. Please try again later.")
            return redirect('add_user')
        except ValueError:
            messages.error(request, "Form values are required.")
            return redirect('add_user')
        
        messages.success(request, f"{user.username} account has been updated successfully.")
        return redirect('all_users')


@require_http_methods(["GET"])
@login_required(login_url='login')
@permission_required(['home.delete_user'], raise_exception=True)
def delete_user(request, user_id):
    clinics = Clinic.objects.none()
    try:
        if request.user.is_superuser:
            user = User.objects.get(custom_id=user_id)
            # also delete clinic if user is clinic admin if you want this functionality
        elif request.user.is_admin:
            user = User.objects.get(custom_id=user_id, clinic=request.user.clinic_id)
            if request.user.id == user.id:
                messages.error(request, "You do not have permission to delete this account.")
        else:
            user = User.objects.none()
    except (User.DoesNotExist, User.MultipleObjectsReturned):
        messages.error(request, "User does not exist with given id.")
    
    if user:
        username = user.username
        user.delete()
        messages.success(request, f"{username} account deleted successfully.")
    return redirect('all_users')


@require_http_methods(["POST"])
@login_required(login_url='login')
@permission_required(['home.change_user'], raise_exception=True)
def update_user_status(request):
    custom_id = request.POST.get('user_id')
    try:
        status = int(request.POST.get('status',''))
        if not (status == 0 or status == 1):
            raise ValueError("Value must be 0 or 1")
    except (ValueError, TypeError):
        return HttpResponseBadRequest()
        
    active,msg = (True, "'{}' account activated successfully.") if status else (False, "'{}' account deactivated successfully.")
    try:
        if request.user.is_superuser:
            user = User.objects.get(custom_id=custom_id)
        elif request.user.is_admin:
            if not request.user.clinic:
                messages.error(request, "You do not have registerd clinic details.")
                return redirect('all_users')
            else:
                user = User.objects.get(custom_id=custom_id, clinic=request.user.clinic_id)
                if request.user.id == user.id:
                    messages.error(request, "You do not have permission to deactivate this account.")
        else:
            return HttpResponseForbidden(forbidden_message)
        user.is_active = active
        user.save()
        messages.info(request, msg.format(user.username))
    except (User.DoesNotExist, User.MultipleObjectsReturned):
        messages.error(request, "User not exist with given id.")
    except IntegrityError:
        messages.error(request, "Status not updated.Please try again.")
    return redirect('all_users')   


@require_http_methods(['GET', 'POST'])
@login_required(login_url='login')
def profile(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name',)
        last_name = request.POST.get('last_name')

        user = request.user # User.objects.get(username=request.user.username)
        user.first_name = first_name
        user.last_name = last_name

        if 'profile_img' in request.FILES:
            profile_img = request.FILES['profile_img']
            if user.profile_img:
                default_storage.delete(user.profile_img.path)
            user.profile_img = profile_img

        user.save()
        messages.success(request, f'{user.username} Profile updated successfully.')
        return redirect('profile')

    return render(request, 'profile.html', {'search_bar':"flase"})


@require_http_methods(["GET"])
@login_required(login_url='login')
@permission_required(['home.view_clinic'], raise_exception=True)
def clinic(request):
    clinics = Clinic.objects.none()
    if request.user.is_superuser:
        clinics = Clinic.objects.all()
    return render(request, 'clinic.html', {'clinics':clinics})


@require_http_methods(["GET", "POST"])
@login_required(login_url='login')
@permission_required(['home.add_clinic'], raise_exception=True)
def clinic_add(request):
    if request.user.is_admin and request.user.clinic:
        return redirect('clinic')
    
    if request.method == "GET":
        return render(request, 'clinic_add.html', {'search_bar':"flase"})
    
    if request.method == "POST":
        name = request.POST.get('clinic_name', '').strip()
        email = request.POST.get('email', '').strip()
        number = request.POST.get('number', '').strip()
        address = request.POST.get('address', '').strip()
        state = request.POST.get('state', '')
        city = request.POST.get('city', '')
        pincode = request.POST.get('pincode', '').strip()
        specializations = request.POST.get('specializations', '').strip()
        try:
            cl = Clinic.objects.create(
                name=name,
                email=email,
                number=number,
                address=address,
                pincode=pincode,
                specializations=specializations,
            )
            try:
                state= Region.objects.get(id=state)
                city = City.objects.get(id=city)
            except (Region.DoesNotExist, City.DoesNotExist):
                messages.error(request, "State and City id does not exist.")
                return render(request, 'clinic_add.html', {'search_bar':"flase"})
            
            cl.state = state
            cl.city = city
            cl.save()
            messages.success(request, f"Clinic {cl.name} add successfully.")
        except IntegrityError:
            messages.error(request, "Clinic does not created.")
            return render(request, 'clinic_add.html', {'search_bar':"flase"})
        return redirect("clinic")


@require_http_methods(["GET", "POST"])
@login_required(login_url='login')
@permission_required(['home.change_clinic'], raise_exception=True)
def clinic_edit(request, clinic_id):
    try:
        if request.user.is_superuser:
            clinic = Clinic.objects.get(id=clinic_id)
        elif request.user.is_admin:
            if request.user.clinic and clinic_id == request.user.clinic_id:
                clinic = Clinic.objects.get(id=clinic_id)
            else:
                messages.error(request, 'User does not have clinic.')
                return redirect("clinic")
        else:
            clinic = Clinic.objects.get(id=clinic_id)      
    except (Clinic.DoesNotExist, Clinic.MultipleObjectsReturned):
        messages.error(request, "Clinic does not exist with given id.")
        return redirect("clinic")
    
    if request.method == 'GET':
        return render(request, "clinic_edit.html", {'clinic':clinic, 'search_bar':"flase"})
        
    if request.method == 'POST':
        name        = request.POST.get('clinic_name', '').strip()
        email       = request.POST.get('email', '').strip()
        number      = request.POST.get('number' '').strip()
        address     = request.POST.get('address', '').strip()
        state       = request.POST.get('state', '')
        city        = request.POST.get('city', '')
        pincode     = request.POST.get('pincode', '').strip()   
        specializations = request.POST.get('specializations', '').strip()

        clinic.name     = name
        clinic.email    = email
        clinic.number   = number
        clinic.address  = address
        clinic.pincode  = pincode
        clinic.specializations = specializations
        try:
            if state != clinic.state_id:
                state= Region.objects.get(id=state)
                clinic.state = state
            if city != clinic.city_id:
                city = City.objects.get(id=city)
                clinic.city = city

            clinic.save()
            messages.success(request, f"{clinic.name} Clinic updated successfully.")
        except (Region.DoesNotExist, City.DoesNotExist):
            messages.error(request, "State and City id does not exist.")
            return render(request, 'clinic_edit.html', {'clinic':clinic, 'search_bar':"flase"}) 
        except IntegrityError:
            messages.error(request, "Clinic does not updated.")
            return render(request, 'clinic_edit.html', {'clinic':clinic, 'search_bar':"flase"})  
        return redirect('clinic')


@require_http_methods(["GET"])
@login_required(login_url='login')
@permission_required(['home.delete_clinic'], raise_exception=True)
def clinic_delete(request, clinic_id):
    try:
        if request.user.is_superuser:
            cl = Clinic.objects.get(id=clinic_id)
        elif request.user.is_admin:
            if request.user.clinic and clinic_id == request.user.clinic_id:
                cl = Clinic.objects.get(id=clinic_id)
            else:
                messages.error(request, 'User does not have clinic.')
                return redirect("clinic")
        else:
            cl = Clinic.objects.get(id=clinic_id)
        clinic_name = cl.name
        cl.delete()
        messages.success(request, f'"{clinic_name}" Clinic deleted successfully.')
    except Clinic.DoesNotExist:
        messages.error(request, 'Clinic does not exist with given id.')
    except IntegrityError:
        messages.error(request, 'Error occured in Clinic deletion.')
    return redirect("clinic")


@login_required(login_url='login')
@permission_required(['home.view_patient'], raise_exception=True)
def patients(request):
    if request.method == 'GET':
        patients = Patient.objects.none()
        if request.user.is_superuser:
            patients = Patient.objects.all()
        else:
            if request.user.clinic:
                patients = Patient.objects.filter(clinic=request.user.clinic_id).order_by('-created_at')
        return render(request, 'patitens_list.html', {'patients':patients})
    return HttpResponseBadRequest()


@require_http_methods(['GET', 'POST'])
@login_required(login_url='login')
@permission_required(['home.add_patient'], raise_exception=True)
def add_new_patient(request):        
    if request.method == 'POST':
        name        = request.POST.get('name','').strip()
        age         = request.POST.get('age') or None
        gender      = request.POST.get('gender','').strip()
        number      = request.POST.get('number','').strip()
        address     = request.POST.get('address','').strip()
        medical_history= request.POST.get('medical_history','').strip()
        blood_group = request.POST.get('blood_group','').strip()
        doctor_id   = request.POST.get('doctor')
        clinic_id   = request.POST.get('clinic')

        try:
            if request.user.is_superuser:
                clinic = Clinic.objects.get(id=clinic_id)
                doctor = User.objects.get(custom_id=doctor_id, clinic=clinic_id)
            else:
                if not request.user.clinic:
                    messages.error(request, "You are not register to any clinic.")
                    return redirect('patients')
                else:
                    clinic = Clinic.objects.get(id=request.user.clinic_id)
                    doctor = User.objects.get(custom_id=doctor_id)
        except (User.DoesNotExist, Clinic.DoesNotExist):
            messages.error(request, "Doctor and Clinic id does not exist or Doctor should be in Clinic.")
            return redirect('patients')
        except Exception as e:
            messages.error(request, "Clinic and Doctor does not exist with given id")
            return redirect('patients')
        
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
            messages.success(request, f"Patient {patient.name!r} added successfully.")
            return redirect('patients')
        except IntegrityError:
            messages.error(request, "There is an error with form data.")
    
    # common for POST and GET Methods
    clinics = Clinic.objects.none()
    doctors = User.objects.none()
    if request.user.is_superuser:
        clinics = Clinic.objects.all()
        doctors = User.objects.filter(clinic__isnull=False).values_list('custom_id','username')
    else:
        if not request.user.clinic:
            messages.error(request, "You are not register to any clinic.")
            return redirect('patients')
        else:
            clinics = Clinic.objects.filter(id=request.user.clinic_id)
            doctors = User.objects.filter(clinic__in=clinics).values_list('custom_id','username')
    return render(request, 'add_patient.html', {'clinics':clinics, 'doctors':doctors, 'search_bar':"flase"})


@require_http_methods(['GET', 'POST'])
@login_required(login_url='login')
@permission_required(['home.change_patient'], raise_exception=True)
def edit_patient(request, patient_id):
    clinics = Clinic.objects.none()
    doctors = User.objects.none()
    if request.user.is_superuser:
        patient = get_object_or_404(Patient, id=patient_id)
        clinics = Clinic.objects.all()
        doctors = User.objects.filter(clinic__isnull=False).values_list('custom_id','username','id')
    else:
        if not request.user.clinic:
            messages.error(request, "You are not register to any clinic.")
            return redirect('patients')
        else:
            patient = get_object_or_404(Patient, id=patient_id, clinic=request.user.clinic_id)  #for specific doctor=request.user_id 
            clinics = Clinic.objects.filter(id=request.user.clinic_id)
            doctors = User.objects.filter(clinic__in=clinics).values_list('custom_id','username','id')

    if request.method == 'GET':
        return render(request, 'edit_patient.html', {'patient':patient, 'clinics':clinics, 'doctors':doctors, 'search_bar':"flase"})

    if request.method == 'POST':
        name        = request.POST.get('name').strip()
        age         = request.POST.get('age').strip()
        gender      = request.POST.get('gender').strip()
        number      = request.POST.get('number').strip()
        address     = request.POST.get('address').strip()
        medical_history = request.POST.get('medical_history').strip()
        blood_group = request.POST.get('blood_group').strip()
        image       = request.FILES.get('image')
        doctor_id   = request.POST.get('doctor')
        clinic_id   = request.POST.get('clinic')
        
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
            
            if request.user.is_superuser:
                if patient.clinic_id != clinic_id:
                    cl = Clinic.objects.get(id=clinic_id)
                    patient.clinic = cl
                if patient.doctor_id != doctor_id:
                    patient.doctor = User.objects.get(custom_id=doctor_id, clinic=cl.id)
            else:
                if not request.user.clinic:
                    messages.error(request, "You are not register to any clinic.")
                    return redirect('patients')
                else:
                    if patient.doctor_id != doctor_id:
                        patient.doctor = User.objects.get(custom_id=doctor_id, clinic=request.user.clinic_id)
                    # clinic = Clinic.objects.get(id=request.user.clinic_id) #clinic would be same so no need to change
            
            patient.save()
            messages.success(request, f"Patient {patient.name!r} updates successfully.")
            return redirect('patients')
        except (User.DoesNotExist, Clinic.DoesNotExist):
            messages.error(request, "Doctor and Clinic id does not exist or Doctor should be in Clinic.")
        except IntegrityError:
            messages.error(request, "There is an error with form data.")
        except Exception as error:
            messages.error(request, "There is an error with form data.")
        return render(request, 'edit_patient.html', {'patient':patient, 'clinics':clinics, 'doctors':doctors, 'search_bar':"flase"})
        

@require_http_methods(['GET'])
@login_required(login_url='login')
@permission_required(['home.delete_patient'], raise_exception=True)
def delete_patient(request, patient_id):
    try:
        patient = None
        if request.user.is_superuser:
            patient = Patient.objects.get(id=patient_id)
        else:
            if not request.user.clinic:
                messages.error(request, "You are not register to any clinic.")
                return redirect('patients')
            else:
                patient = Patient.objects.get(id=patient_id, clinic=request.user.clinic_id)
        if patient:
            patient_name = patient.name
            patient.delete()
            messages.success(request, f"Patient {patient_name!r} records deleted successfully.")
    except Patient.DoesNotExist:
        messages.error(request, f"Patient does not exist with given id.") 
    except IntegrityError:
        messages.error(request, "Error occurred in patient record deletion.")        
    return redirect ('patients')


@require_http_methods(['GET'])
@login_required(login_url='login')
def patient_details(request, patient_id):
    if request.method == 'GET':
        patient = Patient.objects.none()
        prescriptions = Prescription.objects.none()

        if request.user.is_superuser:
            patient = Patient.objects.filter(id=patient_id).first()
        elif request.user.is_admin:
            patient = Patient.objects.filter(id=patient_id, clinic=request.user.clinic_id).first()
        elif request.user.is_admin_staff:
            patient = Patient.objects.filter(id=patient_id, clinic=request.user.clinic_id).first()
        else:
            return HttpResponseForbidden("You do not have permission to this source.")

        if patient:
            prescriptions = Prescription.objects.filter(patient=patient).order_by('visit_date')
        
        context = {
            'patient': patient,
            'prescriptions' : prescriptions,
        }
        return render(request, 'patient_details.html', context)


@login_required(login_url='login')
def add_patient_visit(request, patient_id):
    today = now().date()
    today = today.strftime("%Y-%m-%d")

    if request.method == 'GET':
        return render(request, 'add_patient_visit.html', {'today': today})
    
    if request.method == 'POST':
        if request.user.is_admin:
            pass
        patient = get_object_or_404(Patient, id=patient_id)

        symptoms = request.POST.get('symptoms')
        prescription = request.POST.get('prescription')
        visit_date = request.POST.get('visit_date',)
        next_visit = request.POST.get('next_visit') or None
        image = request.FILES.get('image')
        amount = request.POST.get('amount',0)
        paid_amount = request.POST.get('paid_amount',0)
        
        try:
            amount = abs(int(amount))
            paid_amount = abs(int(paid_amount))
            pending_amount = amount - paid_amount
        except ValueError:
            messages.error(request, "amount value is not an integer")
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
                    patient     = patient,
                    symptoms    = symptoms,
                    prescription= prescription,
                    visit_date  = visit_date,
                    next_visit  = next_visit,
                    amount      = amount,
                    pending_amount= pending_amount,
                    status      = status
                )
                if image:    
                    prescription.image = image
                    prescription.save()
        except Exception as e:
            messages.error(request, f"Error occurred: {str(e)}")
        else:
            messages.success(request, f"{patient.name!r} new visit added successfully.")

        return redirect('patient_details', patient_id=patient_id)


@require_http_methods(["GET", "POST"])
@login_required(login_url='login')
def edit_patient_visit(request, patient_id, visit_id):
    today = now().date()
    today = today.strftime("%Y-%m-%d")

    if request.method == 'GET':
        prs = Prescription.objects.filter(id=visit_id).first()
        return render(request, 'edit_patient_visit.html', {'today': today, 'prs':prs, 'patient_id':patient_id, 'visit_id':visit_id})
    
    if request.method == 'POST':        
        if request.user.is_admin or request.user.is_admin_staff:
            doctor = request.user
            clinic = request.user.clinic

        patient     = get_object_or_404(Patient, id=patient_id, doctor=doctor)  #patinet of perticuler doctor
        prs         = get_object_or_404(Prescription, id=visit_id, patient=patient) #prescription of perticuler 
        symptoms    = request.POST.get('symptoms')
        prescription= request.POST.get('prescription')
        visit_date  = request.POST.get('visit_date')
        next_visit  = request.POST.get('next_visit') or None
        image       = request.FILES.get('image')
        amount      = request.POST.get('amount',0)
        paid_amount = request.POST.get('paid_amount',0)
        
        try:
            amount      = abs(int(amount))
            paid_amount = abs(int(paid_amount))
            pending_amount= amount - paid_amount
        except ValueError:
            messages.error(request, "amount value is not integer")
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
                prs.amount = amount
                prs.pending_amount = pending_amount
                prs.status = status
                if image:
                    if prs.image:
                        os.remove(prs.image.path)
                    prs.image = image
                prs.save()
        except Exception as e:
            messages.error(request, f"Error occurred: {str(e)}")
        else:
            messages.success(request, "Visit updated successfully.")
        return redirect('patient_details', patient_id=patient_id)


@require_http_methods(['GET'])
@login_required(login_url='login')
def clear_pending_payment(request, patient_id, visit_id):
    """ Clear Pending payment """
    clinic = request.user.clinic
    doctor = request.user
    if request.user.is_superuser:
        patient = get_object_or_404(Patient, id=patient_id)
    elif request.user.is_admin:
        patient = get_object_or_404(Patient, id=patient_id, clinic=clinic)
    elif request.user.is_admin_staff:
        patient = get_object_or_404(Patient, id=patient_id, clinic=clinic, doctor=doctor)
    else:
        return HttpResponseForbidden("You are not allowed to acced this page.")
    
    prs = get_object_or_404(Prescription, id=visit_id, patient=patient)
    prs.pending_amount = 0
    prs.status = "Paid"
    prs.save()
    messages.success(request, f"{patient.name} pending payment clear successfylly.")
    return redirect ('patient_details', patient_id=patient_id)


@require_http_methods(['GET'])
@login_required(login_url='login')
def delete_patient_visit(request, patient_id, visit_id):
    """ delete perticuler visit of patient """
    clinic = request.user.clinic
    doctor = request.user
    
    if request.user.is_superuser:
        patient = get_object_or_404(Patient, id=patient_id)
    elif request.user.is_admin:
        patient = get_object_or_404(Patient, id=patient_id, clinic=clinic)
    elif request.user.is_admin_staff:
        patient = get_object_or_404(Patient, id=patient_id, clinic=clinic, doctor=doctor)
    else:
        return HttpResponseForbidden("You are not allowed to acced this page.")
    
    prs = get_object_or_404(Prescription, id=visit_id, patient=patient) #perticuler prescription of patient 
    prs.delete()
    messages.success(request, "Visit deleted successfully.")
    return redirect ('patient_details', patient_id=patient_id)


@require_http_methods(["GET", "POST"])
@login_required(login_url='login')
def notes(request, note_id=None):
    """ send notification to users and view all notes """

    u_emails = []
    if request.user.is_superuser:
        u_emails = User.objects.filter(is_active=True).exclude(id=request.user.id).values_list('email', flat=True)
    elif request.user.is_admin or request.user.is_admin_staff:
        u_emails = User.objects.filter(Q(is_superuser=True) | Q(clinic=request.user.clinic_id), is_active=True).exclude(id=request.user.id).values_list('email', flat=True)

    if request.method == 'POST':
        subject = request.POST.get('subject','')
        recipients = request.POST.getlist('recipients', [])
        # message = request.POST.get('message','')

        if subject and recipients:
            recipients = [ r.strip().lower() for r in recipients ]
            
            if request.user.email in recipients:
                recipients.remove(request.user.email)

            if request.user.is_superuser:
                receiver = User.objects.filter(email__in=recipients, is_active=True)
            elif request.user.is_admin or request.user.is_admin_staff:
                receiver = User.objects.filter(Q(is_superuser=True) | Q(clinic=request.user.clinic_id), email__in=recipients, is_active=True)
            
            if not receiver.count() == 0:
                note = Notification.objects.create(
                    sender = request.user,
                    subject = subject,
                    # message = message
                )
                note.receiver.set(receiver)
                note.save()
                messages.success(request, "Notification sent successfully.")
            else:
                messages.error(request, "No valid recipient found.")
        else:
            messages.error(request, "All fields are required.")

    # common for get and post method
    if request.user.is_superuser:
        note_obj = Notification.objects.all().prefetch_related("sender", "receiver").order_by('-created_at')
    else:
        note_obj = Notification.objects.filter(sender=request.user).prefetch_related("sender", "receiver").order_by('-created_at')
    
    notes = [{
            "id": note.id,
            "subject": note.subject,
            # "message": note.message,
            "sender": note.sender.email,
            "receivers": list(note.receiver.values_list("email", flat=True)),
            "created_at": note.created_at
        } for note in note_obj]
    return render(request, 'notifications.html', {'notes':notes, 'users':u_emails})


@require_http_methods(['GET'])
@login_required(login_url='login')
def delete_note(request, note_id):
    """ delete perticuler notification """

    if not note_id:
        messages.error(request, "Notification id is required.")
    else:
        if request.user.is_superuser:
            note = Notification.objects.filter(id=note_id).first()
        else:
            note = Notification.objects.filter(id=note_id, sender=request.user).first()
        
        if note:
            note.delete()
            messages.success(request, "Notification deleted successfully.")
        else:
            messages.error(request, "Notification not found.")
        return redirect('notifications')


@require_http_methods(['GET'])
@login_required(login_url='login')
def getReceiveNotifications(request):
    """ fetch all notifications of logged in user """
    seen_count = 0
    unseen_count = 0
    notes = (
        Notification.objects.filter(receiver=request.user)
        .annotate(is_seen=Exists(
            SeenNotification.objects.filter(
                note=OuterRef('pk'),
                seen_by=request.user
            )
        )).order_by('-created_at')
        .values('id', 'subject', 'sender__email', 'sender__username', 'sender__profile_img', 'is_seen', 'created_at')
    )
    if notes.exists():
        n = [{
            "id": note['id'],
            "subject": note['subject'],
            # "message": note['message'],
            "sender_email": note['sender__email'],
            "sender_username": note['sender__username'],
            'sender_profile_img': note['sender__profile_img'] if note['sender__profile_img'] else None,
            "is_seen": note['is_seen'],
            "created_at": note['created_at'].strftime("%d-%b-%Y")

        } for note in notes ]
    return JsonResponse({'notes':n}, status=200)
        

@require_http_methods(['GET'])
@login_required(login_url='login')
def markSeenNotification(request, note_id):
    if note_id:
        notification = Notification.objects.filter(id=note_id, receiver=request.user).first()
        if notification:
            seen_note, created = SeenNotification.objects.get_or_create(
                note=notification,
                seen_by=request.user,
            )
            if created:
                return JsonResponse({'marked': True, 'message': "success"}, status=200)
            else:
                return JsonResponse({'marked': False, 'message': "allredy marked"}, status=200)
        else:
            return JsonResponse({'message': 'Notification not found.'}, status=404)
    else:
        return JsonResponse({'message': 'Bad request.'}, status=400)


@require_http_methods(['GET'])
@login_required(login_url='login')
def check_unique(request):
    """ check email or username or group name is unique. """

    if request.method == 'GET':
        field = request.GET.get('field', '')
        value = request.GET.get('value', '')
        exists = None
        message = None

        if field == 'email':
            value = value.strip()
            exists = User.objects.filter(email=value).exists()  
        elif field == 'username':
            value = value.strip()
            exists = User.objects.filter(username=value).exists()
        elif field == 'group_name':
            value = value.strip().lower().replace(" ","_")
            exists = Group.objects.filter(name=value).exists()
        elif field == "clinic_name":
            value = value.strip()
            exists = Clinic.objects.filter(name=value).exists()

        message = f"{field} is not available" if exists == True else f"{field} is available"
        return JsonResponse({'exists':exists, 'message':message}, status=200)


@login_required(login_url='login')
def get_users(request):
    if request.method == 'GET':
        x = lambda users: [user for user in users]
        users = []
        if request.user.is_superuser:
            users = x(   
                User.objects.filter(is_active=True)
                .exclude(id=request.user.id)
                .values_list('email',)
            )
        elif request.user.is_admin or request.user.is_admin_staff:
            users = x(
                User.objects.filter(Q(is_superuser=True) | Q(clinic=request.user.clinic_id), is_active=True)
                .exclude(id=request.user.id)
                .values_list('email',)
            )
        return JsonResponse({'data': users}, status=200) 
    return JsonResponse({'data': []}, status=400)


# content_type = ContentType.objects.get_for_model(MyModel)
# permissions = Permission.objects.filter(content_type=content_type)
# app_label = Group._meta.app_label
# model_name = Group._meta.model_name
# print(f"{app_label}.view_{model_name}")

@require_http_methods(['GET'])
@login_required(login_url='login')
@permission_required(['auth.view_group'], raise_exception=True)
def groups(request):
    groups = Group.objects.all()
    return render(request, 'groups.html', {'groups':groups})


@require_http_methods(['GET','POST'])
@login_required(login_url='login')
@permission_required(['auth.add_group'], raise_exception=True)
def groups_add(request):
    permissions = Permission.objects.all()
    if request.method == "GET":
        return render(request, 'groups_add.html', {'permissions':permissions})
        
    if request.method == "POST":
        group_name = request.POST.get('name','').strip().lower().replace(" ", "_")
        choosen_p = request.POST.getlist('permissions', [])
        choosen_permission = []
        for cp in choosen_p:
            try:
                cp =int(cp)
                choosen_permission.append(cp)
            except (TypeError, ValueError):
                pass

        per_objs = Permission.objects.filter(id__in=choosen_permission) if choosen_permission else []
        try:
            group = Group.objects.create(name=group_name)
            if per_objs:
                group.permissions.set(per_objs)    # group.permissions.add(*per_objs)
                group.save()
            messages.success(request, f"Group {group.name} created successfully.")
        except IntegrityError:
                messages.error(request, f"Error occured in Group creation.")
        return redirect('groups')
        


@require_http_methods(['GET','POST'])
@login_required(login_url='login')
@permission_required(['auth.change_group'], raise_exception=True)
def groups_edit(request, id):
    try:
        group           = Group.objects.get(id=id)
        permissions     = Permission.objects.all()
        group_permissions= Permission.objects.filter(group=group.id)
    except (Group.DoesNotExist, Group.MultipleObjectsReturned):
        messages.error(request, f"Group does not exist with given {id=}.")
        return redirect('groups')
    
    if request.method == "GET":
        permissions = permissions.exclude(id__in=group_permissions)
        return render(request, 'groups_edit.html', {'group':group, 'permissions':permissions, 'group_permissions':group_permissions})
    
    if request.method == "POST":
        group_name = request.POST.get('name', '').strip().lower().replace(" ", "_")
        choosen_p = request.POST.getlist('permissions', [])
        choosen_permission = []
        
        for cp in choosen_p:
            try:
                cp =int(cp)
                choosen_permission.append(cp)
            except (TypeError, ValueError):
                pass
        
        per_objs = Permission.objects.filter(id__in=choosen_permission) if choosen_permission else []
        try:
            if per_objs:
                group.permissions.set(per_objs)
            else:
                group.permissions.clear()
            group.name = group_name
            group.save()
            messages.success(request, f"Group {group.id} Updated successfully.")
        except IntegrityError:
            messages.error(request, f"Error occured in Group {group.id} updation.")
        return redirect('groups')


@require_http_methods(['GET'])
@login_required(login_url='login')
@permission_required(['auth.delete_group'], raise_exception=True)
def groups_delete(request, id):
    try:
        group = Group.objects.get(id=id)
    except (Group.DoesNotExist, Group.MultipleObjectsReturned):
        messages.error(request, f"Group does not exist with given {id=}.")
    group_id = group.id
    group.delete()
    messages.success(request, f"Group id={group_id} deleted successfully.")
    return redirect('groups')


# fetch("/staffs/")
#   .then(response => {
#     if (!response.ok) {
#       throw new Error("Network response was not ok " + response.statusText);
#     }
#     return response.json(); // convert response to JSON
#   })
#   .then(data => {
#     console.log("Post Data:", data);
#   })
#   .catch(error => {
#     console.error("Fetch error:", error);
#   });

# async function getData() {
#   const response = await fetch("https://jsonplaceholder.typicode.com/posts/1");
#   const data = await response.json();
#   console.log("Data:", data); // ✅ actual data
# }
