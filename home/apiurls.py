from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from rest_framework import routers
from rest_framework.authtoken import views as rest_views


from .api import *

# from rest_framework_simplejwt.views import (
#     TokenObtainPairView,
#     TokenRefreshView,
# )


# urlpatterns = [
#     path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Issue access/refresh tokens
#     path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Refresh access token
# ]

urlpatterns = [
    path('login/', LoginApiView.as_view(), name="login"),
    path('logout/', LogoutApiView.as_view(), name='logout'),
    # path('send_otp/', send_otp_email, name='send_otp'),
    # path('verify_otp/', verify_otp, name='verify_otp'),
    # path('reset_password/', reset_password, name='reset_password'),
    

]