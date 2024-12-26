from djoser.serializers import UserCreateSerializer
from .models import UserAccount
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


class UserCreateSerializer(UserCreateSerializer):
    class Meta (UserCreateSerializer.Meta):
        model = UserAccount
        fields= ('id', 'email', 'password', 'username')

class UserOTPSerializer(serializers.ModelSerializer):
    otp = serializers.CharField(max_length=6)

    class Meta:
        model = UserAccount
        fields = ['otp']

class UserAccountSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = UserAccount
        fields = ['id', 'email', 'password', 'username']
        extra_kwargs = {'password': {'write_only': True}}
        error_messages = {
            'email': {
                'invalid': ("Enter a valid email."),
                'unique': ("user with this email address already exists.")
            },
        }
        

    def validate_email(self, value):
        if UserAccount.objects.filter(email=value).exists():
            raise serializers.ValidationError()
        return value

    def validate_password(self, value):
        validate_password(value)
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("Password must contain at least one digit.")
        if not any(char in "!@#$%^&*()-_=+[{]}\\|;:'\",<.>/?`~" for char in value):
            raise serializers.ValidationError("Password must contain at least one special character.")
        return value

    def create(self, validated_data):
        user = UserAccount.objects.create_user(**validated_data)
        return user
    
    def validate(self, attrs):
        # Performing otp validation
        email = attrs.get('email')
        otp = attrs.get('otp')

        try:
            user = UserAccount.objects.get(email=email)
        except UserAccount.DoesNotExist:
            raise serializers.ValidationError({'error': 'User with this email does not exist.'})
        
        if user.otp != otp:
            raise serializers.ValidationError({'error': 'Invalid OTP.'})
        
        # Resetting the OTP field after successful validation
        user.otp = None
        user.save()

        return attrs