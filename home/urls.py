from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.index, name='home'),
    path('login/', views.login_in, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('forget-password/', views.forget_password, name='forget_password'),
    path('reset-password/<str:token>/', views.reset_password, name='reset_password'),
    path('otp-verification/<int:id>/', views.otp_verification, name='otp_verification'),
    path('change-password/', views.change_password, name='change_password'),
    path('change-user-password/', views.change_user_password, name='change_user_password'),

    path('profile/', views.profile, name='profile'),
    path('clinic/', views.clinic, name='clinic'),
    path('patients/', views.patients, name='patients'),
    path('add-new-patient/', views.add_new_patient, name='add_new_patient'),
    path('patient-details/<int:id>/', views.patient_details, name='patient_details'),
    
    
    path('all-users/', views.all_users, name='all_users'),
    path('country-states/', views.country_states, name='country_states'),
    path('state-cities/<int:region>/', views.state_cities, name='state_cities'),
    

]