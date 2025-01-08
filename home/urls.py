from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.index, name='home'),
    path('login/', views.login_in, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('forget-password/', views.forget_password, name='forget_password'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('otp-verification/<int:id>', views.otp_verification, name='otp_verification'),
    path('change-password/<str:token>/', views.change_password, name='change_password'),

    path('profile/', views.profile, name='profile'),
    path('clinic/', views.clinic, name='clinic'),
    
    path('all_users/', views.all_users, name='all_users'),
    path('country-states/', views.country_states, name='country_states'),
    path('state-cities/<int:region>/', views.state_cities, name='state_cities'),
    

]