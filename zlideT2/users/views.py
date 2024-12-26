from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import AllowAny
from .utils import send_code_to_user, generate_otp, send_otp_email
from django.core.mail import EmailMultiAlternatives
from django.contrib.sites.shortcuts import get_current_site
from .models import UserAccount
from djoser.social.views import ProviderAuthView
from .serializers import UserCreateSerializer, UserOTPSerializer, UserAccountSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
) 
import random


class LoginWithOTP(APIView):
    @extend_schema(
        operation_id='Login With OTP',
        description='This endpoint is used to Login with a One Time Password',
        summary='This endpoint is used to Login with an OTP',
        request= OpenApiTypes.OBJECT,
        responses={200: UserOTPSerializer},
    )
    def post(self, request):
        email = request.data.get('email', '')
        try:
            user = UserAccount.objects.get(email=email)
        except UserAccount.DoesNotExist:
            return Response({'error': 'User with this email does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        
        otp = generate_otp()
        user.otp = otp
        user.save()

        send_otp_email(email, otp)

        return Response({'message': 'OTP has been sent to your email.'}, status=status.HTTP_200_OK)
    

class ValidateOTP(APIView):
    @extend_schema(
        operation_id='Validate OTP',
        description='This endpoint is used to validate a One Time Password',
        summary='This endpoint is used to validate OTP',
        request= OpenApiTypes.OBJECT,
        responses={200: UserOTPSerializer},
    )
    def post(self, request):
        email = request.data.get('email', '')
        otp = request.data.get('otp', '')

        try:
            user = UserAccount.objects.get(email=email)
        except UserAccount.DoesNotExist:
            return Response({'error': 'User with this email does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        
        if user.otp == otp:
            user.otp = None # Resetting the OTP field after successful validation
            user.save()

            # Authenticate the user and create or get an authentication token
            token, _ = Token.objects.get_or_create(user=user)

            return Response({'token': token.key}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)


class CustomProviderAuthView(ProviderAuthView):
    @extend_schema(
        operation_id='Google Authentication',
        description='This endpoint is used to Login with Google',
        summary='This endpoint is used to Login with Google',
        request= OpenApiTypes.OBJECT,
        responses={200: UserCreateSerializer},
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 201:
            access_token = response.data.get('access')
            refresh_token = response.data.get('refresh')

            response.set_cookie(
                'access',
                access_token,
                max_age=settings.AUTH_COOKIE_MAX_AGE,
                path=settings.AUTH_COOKIE_PATH,
                secure=settings.AUTH_COOKIE_SECURE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                samesite=settings.AUTH_COOKIE_SAMESITE
            )
            response.set_cookie(
                'refresh',
                refresh_token,
                max_age=settings.AUTH_COOKIE_MAX_AGE,
                path=settings.AUTH_COOKIE_PATH,
                secure=settings.AUTH_COOKIE_SECURE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                samesite=settings.AUTH_COOKIE_SAMESITE
            )

        return response


class CustomTokenObtainPairView(TokenObtainPairView):
    @extend_schema(
        operation_id='Login with JWT Token',
        description='This endpoint is used to Login with with JWT Token',
        summary='This endpoint is used to Login with JWT Token. The Token is stored using http cookies automatically',
        request= OpenApiTypes.OBJECT,
        responses={200: UserCreateSerializer},
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            access_token = response.data.get('access')
            refresh_token = response.data.get('refresh')

            response.set_cookie(
                'access',
                access_token,
                max_age=settings.AUTH_COOKIE_MAX_AGE,
                path=settings.AUTH_COOKIE_PATH,
                secure=settings.AUTH_COOKIE_SECURE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                samesite=settings.AUTH_COOKIE_SAMESITE
            )
            response.set_cookie(
                'refresh',
                refresh_token,
                max_age=settings.AUTH_COOKIE_MAX_AGE,
                path=settings.AUTH_COOKIE_PATH,
                secure=settings.AUTH_COOKIE_SECURE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                samesite=settings.AUTH_COOKIE_SAMESITE
            )

        return response


class CustomTokenRefreshView(TokenRefreshView):
    @extend_schema(
        operation_id='Refresh JWT Token',
        description='This endpoint refreshes the JWT Token',
        summary='This endpoint is used to refresh the JWT Token. The Token is then stored using http cookies automatically',
        request= OpenApiTypes.OBJECT,
        responses={200: UserCreateSerializer},
    )
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh')

        if refresh_token:
            request.data['refresh'] = refresh_token

        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            access_token = response.data.get('access')

            response.set_cookie(
                'access',
                access_token,
                max_age=settings.AUTH_COOKIE_MAX_AGE,
                path=settings.AUTH_COOKIE_PATH,
                secure=settings.AUTH_COOKIE_SECURE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                samesite=settings.AUTH_COOKIE_SAMESITE
            )

        return response


class CustomTokenVerifyView(TokenVerifyView):
    @extend_schema(
        operation_id='Verify JWT Token',
        description='This endpoint verifies the JWT Token',
        summary='This endpoint is used to verify the JWT Token. The Token is then stored using http cookies automatically',
        request= OpenApiTypes.OBJECT,
        responses={200: UserCreateSerializer},
    )
    def post(self, request, *args, **kwargs):
        access_token = request.COOKIES.get('access')

        if access_token:
            request.data['token'] = access_token

        return super().post(request, *args, **kwargs)


class LogoutView(APIView):
    @extend_schema(
        operation_id='Logout Endpoint',
        description='This endpoint logs out the user by deleting the cookie from the browser.',
        summary='This endpoint logs out the user by deleting the cookie from the browser.',
        request= OpenApiTypes.OBJECT,
        responses={200: UserCreateSerializer},
    )
    def post(self, request, *args, **kwargs):
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie('access')
        response.delete_cookie('refresh')

        return response
    

class CreateUserView(generics.CreateAPIView):
    queryset = UserAccount.objects.all()
    serializer_class = UserAccountSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        operation_id='Create a user using a One-Time Password',
        description='This endpoint creates a user using OTP',
        summary='This endpoint is used to create a user using OTP',
        request= OpenApiTypes.OBJECT,
        responses={200: UserAccountSerializer},
        )
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        # def generate_otp():
        #     return str(random.randint(100000, 999999))
        if serializer.is_valid():
            user = serializer.save(is_active=False)
            otp = random.randint(100000, 999999)
            user.otp = otp
            user.save()

            email = user.email
            current_site = get_current_site(request)
            subject = 'Kindly activate your account'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = user.email
            email.send()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ActivateUserView(APIView):
    permission_classes = [AllowAny]
    @extend_schema(
        operation_id='Activate a user using a One-Time Password',
        description='This endpoint activates a user using OTP',
        summary='This endpoint is used to activate a user using OTP',
        request= OpenApiTypes.OBJECT,
        responses={200: UserAccountSerializer},
        )
    
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        otp = request.data.get('otp')

        if not email or not otp:
            return Response({'error': ('Email and OTP are required.')}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = UserAccount.objects.get(email=email)
        except UserAccount.DoesNotExist:
            return Response({'error': ('User does not exist.')}, status=status.HTTP_400_BAD_REQUEST)
        

        if user.otp == otp:
            user.is_active = True
            user.otp = None # Clear OTP after successful activation
            user.save()

            email = user.email
            current_site = get_current_site(self.request)
            subject = 'Your account has been activated successfully'
            protocol = 'https' if self.request.is_secure() else 'http'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = user.email

            email = EmailMultiAlternatives(subject, from_email, [to_email])
            email.send()

            return Response({'message': ('Your account has been activated successfully')}, status=status.HTTP_200_OK)
        else:
            return Response({'error': ('Invalid OTP.')}, status=status.HTTP_400_BAD_REQUEST)


class ResendOTPView(APIView):
    permission_classes = [AllowAny]
    @extend_schema(
        operation_id='Resend OTP to user',
        description='This endpoint resends OTP to user',
        summary='This endpoint is used to resend OTP to user provided they have their email address.',
        request= OpenApiTypes.OBJECT,
        responses={200: UserAccountSerializer},
        )

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')

        if not email:
            return Response({'error': ('Email is required.')}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = UserAccount.objects.get(email=email)
        except UserAccount.DoesNotExist:
            return Response({'error': ('User does not exist.')}, status=status.HTTP_400_BAD_REQUEST)

        otp = random.randint(100000, 999999)
        user.otp = otp  # Save the OTP to the user model 
        user.save()
        email = user.email
        current_site = get_current_site(self.request)
        subject = 'Your new OTP'
        
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = user.email
        email = EmailMultiAlternatives(subject, from_email, [to_email])
        email.send()

        return Response({'message': ('OTP resent successfully.')}, status=status.HTTP_200_OK)