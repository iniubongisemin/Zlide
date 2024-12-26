import random
import string
from django.core.mail import send_mail
from django.conf import settings

def generate_otp(length=6):
    characters = string.digits
    otp = ''.join(random.choice(characters) for _ in range(length))
    return otp

def send_otp_email(email, otp):
    subject = 'Your OTP for Zlide Login'
    message = f'Your OTP is: {otp}'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list) 


import random
from django.core.mail import EmailMessage
from .models import UserAccount, OneTimePassword
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site

def generateOTP():
    otp = ""
    for i in range(6):
        otp +=str(random.randint(1, 9))
    return otp

def send_code_to_user(email, request):
    Subject = "One time passcode for email verification"
    otp = generateOTP()
    print(otp)
    user = UserAccount.objects.get(email=email)
    current_site = get_current_site(request).domain
    email_body = f"Hi {UserAccount.username} thanks for signing up on {current_site} please verify your email with this \n one time passcode {otp}"
    from_email = settings.DEFAULT_FROM_EMAIL
    # otp_obj = OneTimePassword.objects.create(user=user, otp=otp)

    OneTimePassword.objects.create(user=user, code=otp)

    send_email = EmailMessage(subject=Subject, body=email_body, from_email=from_email, to=[email])
    send_email.send(fail_silently=True)
