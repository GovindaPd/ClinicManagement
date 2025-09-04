from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('rough/', views.rough, name='rough'),
    path('', views.index, name='home'),
    path('check-unique/', views.check_unique, name="check_unique"),
    
    path('login/', views.login_in, name='login'),
    path('logout/', views.logout_user, name='logout'),
    # forget password
    path('password-reset/', views.password_reset, name='password_reset'),                           #step1
    path('password-reset/done/', views.password_reset_done, name="password_reset_done"),            #step2
    path("reset/<uid64>/<token>/", views.password_reset_confirm, name="password_reset_confirm"),   #step3
       
    # path('change-password/', views.change_password, name='change_password'),
    # change user password if user is login
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
    
    # path("password_reset/", 
    #      auth_views.PasswordResetView.as_view(), 
    #      name="password_reset"),
    # path("password_reset/done/", 
    #      auth_views.PasswordResetDoneView.as_view(), 
    #      name="password_reset_done"),
    # path("reset/<uidb64>/<token>/", 
    #      auth_views.PasswordResetConfirmView.as_view(), 
    #      name="password_reset_confirm"),
    # path("reset/done/", 
    #      auth_views.PasswordResetCompleteView.as_view(), 
    #      name="password_reset_complete"),
]