from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.conf import settings

from django.db.models.signals import post_save
from django.dispatch import receiver
class UserManager(BaseUserManager):

    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError("Username is required")
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.Role.ADMIN)
        return self.create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    class Role(models.TextChoices):
        ADMIN   = 'admin',   'Admin'
        MEDECIN = 'medecin', 'Médecin'
        PATIENT = 'patient', 'Patient'

    username   = models.CharField(max_length=150, unique=True)
    email      = models.EmailField(unique=True)
    telephone  = models.CharField(max_length=20, blank=True)
    role       = models.CharField(max_length=10, choices=Role.choices, default=Role.PATIENT)

    is_active  = models.BooleanField(default=True)
    is_staff   = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    reset_code        = models.CharField(max_length=6, blank=True, null=True)
    reset_code_expiry = models.DateTimeField(blank=True, null=True)
    objects = UserManager()

    USERNAME_FIELD  = 'username'            # ✅ login with username
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return f"{self.username} ({self.role})"
    









class Profile(models.Model):
    user      = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    image     = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio       = models.TextField(blank=True)
    address   = models.CharField(max_length=255, blank=True)
    birthdate = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"Profile of {self.user.username}"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()