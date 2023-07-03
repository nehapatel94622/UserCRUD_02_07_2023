from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        Group, PermissionsMixin)
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from rest_framework.authtoken.models import Token
from phonenumber_field.modelfields import PhoneNumberField
from django.core.exceptions import ValidationError
 




# Create your models here.


class AccountManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        values = [email]
        field_value_map = dict(zip(self.model.REQUIRED_FIELDS, values))
        for field_name, value in field_value_map.items():
            if not value:
                raise ValueError("The {} value must be set".format(field_name))

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        Token.objects.create(user=user)
        ProfileModel.objects.create(user=user)
        if extra_fields['is_superuser']:
            adminGroup, _ = Group.objects.get_or_create(name='Admin')
            adminGroup.user_set.add(user)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class UserModel(AbstractBaseUser, PermissionsMixin):
    username = None
    email = models.EmailField(
        verbose_name="email address", max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = AccountManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'



class ProfileModel(models.Model):
    def validate_file_size(value):
        # 1 MB (10  1024  1024 bytes)
        max_size = 1*1024*1024
        if value.size > max_size:
            raise ValidationError("File size should not exceed 1 MB.")
        
    CHOICES = (
        ('english', 'English'),
        ('gujarati', 'Gujarati'),
        ('hindi', 'Hindi'),
    )

    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    designation = models.CharField(max_length=255)
    city = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    profile_pic = models.ImageField(upload_to='media\images', blank=True,null=True, validators=[validate_file_size])
    phone_number = PhoneNumberField(verbose_name="phone number", blank=True, null=True)
    whatsapp_number = PhoneNumberField(blank=True, null=True)
    about_us=models.TextField(blank=True, null=True)
    language_info=models.CharField(max_length=20, choices=CHOICES,default='English')

    
    def __str__(self):
        return str(self.user)

