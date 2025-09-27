from django.urls import path, include
from . import views


urlpatterns = [    
    # core functionality
    path('', views.index, name='home'),
    path('login/', views.login_in, name='login'),
    path('logout/', views.logout_user, name='logout'),
    # forget password in three steps
    path('password-reset/', views.password_reset, name='password_reset'),
    path('password-reset/done/', views.password_reset_done, name="password_reset_done"),
    path("reset/<uid64>/<token>/", views.password_reset_confirm, name="password_reset_confirm"),   
    # change password
    path('change-user-password/', views.change_user_password, name='change_user_password'),
    
    path('profile/', views.profile, name='profile'),
    path('clinic/', views.clinic, name='clinic'),
    path('patients/', views.patients, name='patients'),
    
    path('add-user/', views.add_user, name="add_user"),
    path('edit-user/<str:user_id>/', views.edit_user, name="edit_user"),
    path('update-status/', views.update_user_status, name="update_user_status"),
    path('add-new-patient/', views.add_new_patient, name='add_new_patient'),
    path('patient-details/<int:patient_id>/', views.patient_details, name='patient_details'),
    path('delete-patient/<int:patient_id>/', views.delete_patient, name='delete_patient'),
    path('edit-patient/<int:patient_id>/', views.edit_patient, name='edit_patient'),
    
    path('add-patient-visit/<int:patient_id>/', views.add_patient_visit, name='add_patient_visit'),
    path('edit-patient-visit/<int:patient_id>/<int:visit_id>/', views.edit_patient_visit, name='edit_patient_visit'),
    path('clear-pending-payment/<int:patient_id>/<int:visit_id>/', views.clear_pending_payment, name='clear_pending_payment'),
    path('delete-patient-visit/<int:patient_id>/<int:visit_id>/', views.delete_patient_visit, name='delete_patient_visit'),
    
    path('all-users/', views.all_users, name='all_users'),
    path('country-states/', views.country_states, name='country_states'),
    path('state-cities/<int:region>/', views.state_cities, name='state_cities'),

    path('notifications/', views.notes, name='notifications'),
    path('get-receive-notifications/', views.getReceiveNotifications, name='get_receive_notifications'),
    path('delete-notification/<int:note_id>/', views.delete_note, name='delete_notification'),
    path('mark-as-seen/<int:note_id>/', views.markSeenNotification, name='mark_as_seen'),
    
    path('staffs/', views.get_users, name='get_users'),
    path('check-unique/', views.check_unique, name="check_unique"),
    path('demo/', views.demo)
]

# from django.contrib.auth import views as auth_views
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