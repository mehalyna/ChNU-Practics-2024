import uuid

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class Role(models.TextChoices):
    ADMIN = "admin", "Admin"
    INVESTOR = "investor", "Investor"
    STARTUP = "startup", "Startup"


class CustomUserManager(BaseUserManager):
    def create_user(
        self,
        email: str,
        password: str | None = None,
        **extra_fields,
    ) -> "User":
        if not email:
            raise ValueError("The Email field must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_verified", True)
        extra_fields.setdefault("role", Role.ADMIN)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    USERNAME_FIELD = "email"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=10, default=None, blank=False, null=False)
    username = models.CharField(
        "Username", max_length=64, unique=True, blank=False, null=False
    )
    password = models.CharField("Password", max_length=94, blank=False, null=False)
    email = models.EmailField(
        "Email Address", max_length=320, unique=True, blank=False, null=False
    )

    first_name = models.CharField("First Name", max_length=15, blank=True, null=True)
    last_name = models.CharField("Last Name", max_length=15, blank=True, null=True)

    is_active = models.BooleanField("Active", default=True)
    is_staff = models.BooleanField("Staff Status", default=False)
    is_superuser = models.BooleanField("Superuser Status", default=False)
    is_verified = models.BooleanField("Verified", default=False)

    date_joined = models.DateTimeField("Date Joined", default=timezone.now)

    objects: CustomUserManager = CustomUserManager()

    class Meta:
        verbose_name_plural = "users"
        ordering = ["email"]
        indexes = [models.Index(fields=["email"])]

    def __str__(self) -> str:
        return self.email

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Investor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, on_delete=models.SET_NULL, related_name="investor", null=True
    )
    bio = models.TextField("Bio", max_length=500, blank=True, null=True)
    is_active = models.BooleanField("Active", default=True)

    class Meta:
        verbose_name = "Investor"
        verbose_name_plural = "Investors"
        ordering = ["user"]

    def __str__(self) -> str:
        return str(self.user)


class Founder(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, on_delete=models.SET_NULL, related_name="founder", null=True
    )
    bio = models.TextField("Bio", max_length=500, blank=True, null=True)
    is_active = models.BooleanField("Active", default=True)

    class Meta:
        verbose_name = "Founder"
        verbose_name_plural = "Founders"
        ordering = ["user"]

    def __str__(self) -> str:
        return str(self.user)


@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, **kwargs):
    """Create or update the associated profile when a user is created or updated."""
    investor_profile, _ = Investor.objects.get_or_create(user=instance)
    founder_profile, _ = Founder.objects.get_or_create(user=instance)

    if instance.role == Role.INVESTOR.value:
        investor_profile.is_active = True
        founder_profile.is_active = False
    elif instance.role == Role.STARTUP.value:
        investor_profile.is_active = False
        founder_profile.is_active = True

    investor_profile.save()
    founder_profile.save()
