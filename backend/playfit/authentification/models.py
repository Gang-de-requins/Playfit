import datetime
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, username, password, **extra_fields)

class CustomUser(AbstractUser):
    BODYWEIGHT_STRENGTH = "bodyWeightStrength"
    FAT_LOSS_CARDIO = "fatLossCardio"
    ENDURANCE = "endurance"

    GOALS_CHOICES = [
        (BODYWEIGHT_STRENGTH, "Bodyweight Strength"),
        (FAT_LOSS_CARDIO, "Fat Loss or Cardio"),
        (ENDURANCE, "Endurance"),
    ]

    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    ]

    FITNESS_LEVEL_CHOICES = [
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
    ]

    REGISTRATION_METHOD_CHOICES = [
        ("email", "Email"),
        ("google", "Google"),
    ]

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150, null=True, blank=True)
    last_name = models.CharField(max_length=150, null=True, blank=True)
    password = models.CharField(max_length=150)
    date_of_birth = models.DateField(validators=[MinValueValidator(limit_value=datetime.date.today() - datetime.timedelta(days=365*100)), MaxValueValidator(limit_value=datetime.date.today() - datetime.timedelta(days=365*14))])
    height = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(100), MaxValueValidator(250)])
    weight = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(30), MaxValueValidator(250)])
    goals = models.CharField(max_length=50, choices=GOALS_CHOICES, default=BODYWEIGHT_STRENGTH)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True)
    fitness_level = models.CharField(max_length=20, choices=FITNESS_LEVEL_CHOICES, null=True)
    physical_particularities = models.TextField(null=True)
    last_login = models.DateTimeField(auto_now=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    registration_method = models.CharField(max_length=20, choices=REGISTRATION_METHOD_CHOICES, default="email")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = [
        'email', 'password', 'date_of_birth', 'height', 'weight',
    ]

    def __str__(self):
        return self.username

class Product(models.Model):
    name = models.CharField(max_length=30, null=True,blank=True)
    price = models.CharField(max_length=40,null=True, blank=True)
    quantity = models.IntegerField(blank=True, null=True)