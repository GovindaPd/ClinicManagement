from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema

from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt

from django.db import transaction
from django.contrib.auth.hashers import make_password

from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication


from .models import User, Clinic, Patient, Prescription, Invoice
from .serializers import *
from .tasks import send_email_task
from random import randint


@extend_schema(
    request=(UserLoginSerializer, UserOtpSerializer),
    responses={200: UserSerializer}
)
class LoginApiView(APIView):
    permission_classes = [AllowAny]
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        res = {}
        username = request.data.get('username')
        password = request.data.get('password')
        otp = request.data.get('otp')

        try:
            with transaction.atomic():
                if otp is not None:
                    user = User.objects.filter(otp=otp).first()

                    if user and (user.is_superuser or user.is_doctor):

                        user.otp = None
                        user.save()

                        user.live_login += 1
                        user.is_login = True
                        user.save()

                        if user.live_login > user.max_login_sessions:
                            user.live_login -= 1
                            user.save()
                            res['status'] = False
                            res['message'] = f"Maximum number of allowed login reached ({user.max_login_sessions})"
                            return Response(res, status=status.HTTP_204_NO_CONTENT)
                        
                        res['status'] = True
                        res['message'] = "Login successfully"

                        serializer = UserSerializer(user, read_only=True, context={'request':request}) #UserSerializers(user, read_only=True, context={'request':request})#(instance, data, read_only, write_only, partial,context={'request':request})

                        res['data']  = serializer.data
                        return Response(data=res, status=status.HTTP_200_OK)

                    else:
                        res['status'] = False
                        res['message'] = 'OTP is not valid'
                        return Response(data=res, status=status.HTTP_401_UNAUTHORIZED)
                
                else:
                    user = authenticate(request, username=username, password=password)

                    if username is not None and password is not None and user is None:
                        res['status'] = False
                        res['message'] = 'Invalid Credntionls'
                        return Response(data=res, status=status.HTTP_401_UNAUTHORIZED)
                    
                    if user and (user.is_superuser or user.is_doctor):
                        user.otp = str(randint(10000,99999))
                        user.save()

                        send_email_task(user.email, user.otp)
                        
                        token, created = Token.objects.get_or_create(user=user)
                        res['status'] = True
                        res['message'] = 'Login OTP is sent to your email'
                        return Response(data=res, status=status.HTTP_202_ACCEPTED)
                    
                    
                    else:
                        res['status'] = False
                        res['message'] = 'Invalid Credntionls'
                        return Response(data=res, status=status.HTTP_400_BAD_REQUEST)
                    
        except Exception as e:
            # Handle any unexpected exceptions
            res['status'] = False
            res['message'] = f"Error: {str(e)}"
            return Response(res, status=status.HTTP_205_RESET_CONTENT)



class LogoutApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Delete the authentication token to log the user out
        print("token delete", request.user)
        
        try:
            request.auth.delete()
        except AttributeError as e:
            return Response({'detail': 'Invalid or missing token'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        print(f"----{user}---------")
        user.live_login = max(0, user.live_login-1)
        user.save()
        
        return Response({'detail': 'Logout successful'}, status=status.HTTP_200_OK)

        
