from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
    # User,
    # Permission,
)
from django.contrib.auth import get_user_model



class UserAccountManager(BaseUserManager):
    def create_user(self, email, username, password=None, **kwargs):
        """
        Creates and saves a User with the given email, username and password.
        """
        if not email:
            raise ValueError('Users must have an email address')
        
        if not username:
            raise ValueError("Users must have a username")

        email = self.normalize_email(email) # To convert email to standard email format
        email = email.lower()

        user = self.model(
            email=email,
            username=username,
            **kwargs
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, username, password=None, **kwargs):
        """
        Creates and saves a superuser with the given email, username and password.
        """
        user = self.create_user(
            email,
            password=password,
            username=username,
            **kwargs
        )

        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class UserAccount(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True,)
    username = models.CharField(max_length=255, unique=True)
    otp = models.CharField(max_length=6, null=True, blank=True)

    # groups = models.ManyToManyField(User, related_name='useraccount_groups')  # Added related_name argument
    # groups = models.ManyToManyField(get_user_model(), related_name='useraccount_groups')
    # user_permissions = models.ManyToManyField(Permission, related_name='useraccount_user_permissions')  # Added related_name argument
    # user_permissions = models.ManyToManyField(Permission, related_name='useraccount_user_permissions')  # Added related_name argument

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


class OneTimePassword(models.Model):
    user = models.OneToOneField(UserAccount, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)

    def __str__(self):
        return f"{self.user.username} - otp code"