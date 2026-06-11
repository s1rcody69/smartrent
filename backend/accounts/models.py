import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


# Custom manager that controls how User objects are created
class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        # Enforce that every user must have an email address
        if not email:
            raise ValueError('The Email field must be set')

        # Normalize email — lowercases the domain part (e.g. User@GMAIL.COM → User@gmail.com)
        email = self.normalize_email(email)

        # Create a User instance with the provided email and any extra fields
        user = self.model(email=email, **extra_fields)

        # Hash the password using Django's built-in hashing algorithm
        # Never store raw passwords — set_password() handles this securely
        user.set_password(password)

        # Save the user to the database
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        # Ensure superuser always has is_staff and is_superuser set to True
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        # Reuse create_user to keep creation logic in one place
        return self.create_user(email, password, **extra_fields)


# Custom User model replacing Django's default User
# AbstractBaseUser — provides password hashing and authentication machinery
# PermissionsMixin — adds is_superuser, groups, and user_permissions support
class User(AbstractBaseUser, PermissionsMixin):

    # Define the three roles a user can have in the system
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('landlord', 'Landlord'),
        ('tenant', 'Tenant'),
    )

    # UUID primary key — more secure than sequential integers
    # editable=False prevents it from being changed after creation
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Email is the unique identifier for authentication
    email = models.EmailField(unique=True)

    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

    # Phone number is optional at registration
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    # Role determines what the user can access in the system
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    # is_active=False disables the account without deleting it
    is_active = models.BooleanField(default=True)

    # is_staff controls access to the Django admin panel
    is_staff = models.BooleanField(default=False)

    # is_verified tracks whether the user confirmed their email address
    is_verified = models.BooleanField(default=False)

    # auto_now_add sets this once at creation and never changes it
    date_joined = models.DateTimeField(auto_now_add=True)

    # auto_now updates this timestamp every time the record is saved
    updated_at = models.DateTimeField(auto_now=True)

    # FIX — override groups and user_permissions with custom related_name
    # This resolves the reverse accessor clash with Django's built-in auth.User
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True
    )

    # Tell Django to use our custom manager
    objects = UserManager()

    # Use email instead of username for authentication
    USERNAME_FIELD = 'email'

    # Fields required when creating a superuser via createsuperuser command
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        db_table = 'users'
        ordering = ['-date_joined']

    # FIX — corrected syntax error, missing closing bracket inside f-string
    def __str__(self):
        return f'{self.email} ({self.role})'

    # Property decorator turns this into a readable attribute — user.full_name
    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

class LandlordProfile(models.Model):
    # One-to-one link to User — one user can have one landlord profile
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='landlord_profile'
    )

    # Business details specific to landlords
    business_name = models.CharField(max_length=255, blank=True, null=True)
    business_registration_number = models.CharField(max_length=100, blank=True, null=True)

    # Cloudinary will store the URL of the uploaded profile photo
    profile_photo = models.ImageField(
        upload_to='landlord_photos/',
        blank=True,
        null=True
    )

    bio = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'landlord_profiles'

    def __str__(self):
        return f'LandlordProfile — {self.user.full_name}'


class TenantProfile(models.Model):
    # Choices for employment status
    EMPLOYMENT_STATUS_CHOICES = (
        ('employed', 'Employed'),
        ('self_employed', 'Self Employed'),
        ('student', 'Student'),
        ('unemployed', 'Unemployed'),
        ('retired', 'Retired'),
    )

    # One-to-one link to User — one user can have one tenant profile
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='tenant_profile'
    )

    # Identity and personal details
    national_id = models.CharField(max_length=20, unique=True, blank=True, null=True)

    profile_photo = models.ImageField(
        upload_to='tenant_photos/',
        blank=True,
        null=True
    )

    # Occupation details — important for tenant vetting in Kenya
    occupation = models.CharField(max_length=255, blank=True, null=True)
    employer_name = models.CharField(max_length=255, blank=True, null=True)
    employment_status = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_STATUS_CHOICES,
        blank=True,
        null=True
    )
    

    # Emergency contact — standard requirement for rental agreements in Kenya
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True)
    emergency_contact_relationship = models.CharField(max_length=50, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tenant_profiles'

    def __str__(self):
        return f'TenantProfile — {self.user.full_name}'
    
