from django.urls import path
from . import views


urlpatterns = [    
    path('', views.index, name='index'),
    path('index/', views.index),
    path('login/', views.login_in, name='login'),
    path('logout/', views.logout_user, name='logout'),
    
    # forget password in three steps
    path('password-reset/', views.password_reset, name='password_reset'),
    path('password-reset/done/', views.password_reset_done, name="password_reset_done"),
    path("reset/<uid64>/<token>/", views.password_reset_confirm, name="password_reset_confirm"),
    # change password
    path('change-user-password/', views.change_user_password, name='change_user_password'),
    path('user/profile/', views.profile, name='profile'),

    path('users/', views.all_users, name='all_users'),
    path('user/add/', views.add_user, name="add_user"),
    path('user/edit/<str:user_id>/', views.edit_user, name="edit_user"),
    path('user/delete/<str:user_id>/', views.delete_user, name="delete_user"),
    path('user/update-status/', views.update_user_status, name="update_user_status"),

    path('clinics/', views.clinic, name='clinic'),
    path('clinic/add/', views.clinic_add, name='add_clinic'),
    path('clinic/edit/<int:clinic_id>/', views.clinic_edit, name='edit_clinic'),
    path('clinic/delete/<int:clinic_id>/', views.clinic_delete, name='delete_clinic'),

    path('patients/', views.patients, name='patients'),
    path('patient/add/', views.add_new_patient, name='add_new_patient'),
    path('patient/details/<int:patient_id>/', views.patient_details, name='patient_details'),
    path('patient/edit/<int:patient_id>/', views.edit_patient, name='edit_patient'),
    path('patient/delete/<int:patient_id>/', views.delete_patient, name='delete_patient'),
    
    path('patient/visit/add/<int:patient_id>/', views.add_patient_visit, name='add_patient_visit'),
    path('patient/visit/edit/<int:patient_id>/<int:visit_id>/', views.edit_patient_visit, name='edit_patient_visit'),
    path('patient/visit/delete/<int:patient_id>/<int:visit_id>/', views.delete_patient_visit, name='delete_patient_visit'),
    path('patient/payment/clear/<int:patient_id>/<int:visit_id>/', views.clear_pending_payment, name='clear_pending_payment'),

    path('notifications/', views.notes, name='notifications'),
    path('notifications/receive/', views.getReceiveNotifications, name='get_receive_notifications'),
    path('notifications/delete/<int:note_id>/', views.delete_note, name='delete_notification'),
    path('notifications/mark-as-seen/<int:note_id>/', views.markSeenNotification, name='mark_as_seen'),
    
    path('groups/', views.groups, name="groups"),
    path('groups/add/', views.groups_add, name="groups_add"),
    path('groups/edit/<int:id>/', views.groups_edit, name="groups_edit"),
    path('group/delete/<int:id>/', views.groups_delete, name="groups_delete"),

    path('staffs/', views.get_users, name='get_users'),
    path('check-unique/', views.check_unique, name="check_unique"),

    path('country-states/', views.country_states, name='country_states'),
    path('state-cities/<int:region>/', views.state_cities, name='state_cities'),

    #ckeditor example
    path('ckeditor/', views.ckView, name='ck_view'),
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