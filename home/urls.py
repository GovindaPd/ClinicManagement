from django.urls import path, include
from . import views


urlpatterns = [
    path('rough/', views.rough, name='rough'),
    path('', views.index, name='home'),
    path('check-unique/', views.check_unique, name="check_unique"),
    path('login/', views.login_in, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('forget-password/', views.forget_password, name='forget_password'),
    path('reset-password/<str:token>/', views.reset_password, name='reset_password'),
    path('otp-verification/<int:id>/', views.otp_verification, name='otp_verification'),
    path('change-password/', views.change_password, name='change_password'),
    path('change-user-password/', views.change_user_password, name='change_user_password'),

    path('add-user/', views.add_user, name="add_user"),
    path('update-status/', views.update_user_status, name="update_user_status"),
    
    path('profile/', views.profile, name='profile'),
    path('clinic/', views.clinic, name='clinic'),
    path('patients/', views.patients, name='patients'),
    path('add-new-patient/', views.add_new_patient, name='add_new_patient'),
    path('patient-details/<int:patient_id>/', views.patient_details, name='patient_details'),
    path('delete-patient/<int:patient_id>/', views.delete_patient, name='delete_patient'),
    path('edit-patient/<int:patient_id>/', views.edit_patient, name='edit_patient'),
    
    path('add-patient-visit/<int:patient_id>/', views.add_patient_visit, name='add_patient_visit'),
    path('edit-patient-visit/<int:patient_id>/<int:visit_id>/', views.edit_patient_visit, name='edit_patient_visit'),
    path('delete-patient-visit/<int:patient_id>/<int:visit_id>/', views.delete_patient_visit, name='delete_patient_visit'),
    
    
    
    path('all-users/', views.all_users, name='all_users'),
    path('country-states/', views.country_states, name='country_states'),
    path('state-cities/<int:region>/', views.state_cities, name='state_cities'),
    

]