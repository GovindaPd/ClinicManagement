from django.urls import path
from . import views

# app_name = 'bahikhata'

urlpatterns = [    
    path('', views.bahikhata, name='bahikhata'),
    path('add/', views.add_bahikhata, name='add_bahikhata'),
    path('update/<int:id>/', views.update_bahikhata, name='update_bahikhata'),
    path('delete/<int:id>/', views.update_bahikhata, name='delete_bahikhata'),

    path('product-list/', views.product_list, name='product_list'),
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
