from django.urls import path, re_path
from .views import (
    CustomProviderAuthView,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    CustomTokenVerifyView,
    LogoutView,
    LoginWithOTP,
    ValidateOTP,
    ActivateUserView,
    ResendOTPView,
)

urlpatterns = [
    re_path(
        r'^o/(?P<provider>\S+)/$',
        CustomProviderAuthView.as_view(),
        name='provider-auth'
    ),
    path('jwt/create/', CustomTokenObtainPairView.as_view()),
    path('jwt/refresh/', CustomTokenRefreshView.as_view()),
    path('jwt/verify/', CustomTokenVerifyView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('login-with-otp/', LoginWithOTP.as_view(), name='login-with-otp'),
    path('activate/', ActivateUserView.as_view(), name='activate'),
    path('resend-otp/', ResendOTPView.as_view(), name='send-otp'),
    path('validate-otp/', ValidateOTP.as_view(), name='validate-otp')
]   