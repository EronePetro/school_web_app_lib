from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.db import models


class CustomAccountManager(BaseUserManager):
    def create_user(self, full_name, email, password, **other_fields):
        if not email:
            raise ValueError('Email must be provided')

        
        email = self.normalize_email(email)

        user = self.model(full_name=full_name, email=email, **other_fields)

        user.set_password(password)

        user.save()

        return user

    
    def create_superuser(self, full_name, email, password, **other_fields):
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)


        if other_fields.get('is_staff') is not True:
            raise ValueError('Super user must be assigned is_staff=True')

        if other_fields.get('is_superuser') is not True:
            raise ValueError('Super user must be set to is_superuser=True')


        return self.create_user(full_name, email, password, **other_fields)



class User(AbstractBaseUser, PermissionsMixin):
    full_name = models.CharField(max_length=60)
    email = models.EmailField(max_length=60, unique=True)
    date_joined = models.DateTimeField(default=timezone.now)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_librarian = models.BooleanField(default=False)
    is_classteacher = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)



    objects = CustomAccountManager()

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['full_name']


    def __str__(self):
        return self.full_name