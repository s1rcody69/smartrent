from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import LandlordProfile, TenantProfile

# Always use get_user_model() instead of importing User directly
# This ensures we always get the active custom user model
User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    # write_only=True means password is accepted on input but never returned in responses
    password = serializers.CharField(write_only=True, min_length=8)
    # confirm_password is only used for validation — not a model field
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'role',
            'password',
            'confirm_password',
        ]

    def validate_email(self, value):
        # Normalize email to lowercase before checking uniqueness
        value = value.lower()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return value
    
    def validate_phone_number(self, value):
        if not value:
          return value

    # Normalize common formats to 2547XXXXXXXX before validating
        cleaned = value.strip().replace(' ', '').replace('-', '')

        if cleaned.startswith('+'):
          cleaned = cleaned[1:]
        if cleaned.startswith('0'):
          cleaned = '254' + cleaned[1:]
        elif cleaned.startswith('7') or cleaned.startswith('1'):
          cleaned = '254' + cleaned

    # A valid Kenyan mobile number is 254 followed by 9 digits, always 12 digits total
        if not cleaned.isdigit() or len(cleaned) != 12 or not cleaned.startswith('254'):
          raise serializers.ValidationError(
            'Enter a valid Kenyan phone number, e.g. 0712345678 or 254712345678.'
        )

        return cleaned
 
    def validate(self, data):
        # Cross-field validation — compare password and confirm_password
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'Passwords do not match.'})
        return data

    def create(self, validated_data):
        # Remove confirm_password before creating the user — it is not a model field
        validated_data.pop('confirm_password')

        # Use create_user() to ensure password is hashed correctly
        user = User.objects.create_user(**validated_data)
        
        # Create the appropriate profile based on the user's role
        if user.role == 'landlord':
            LandlordProfile.objects.create(user=user)
        elif user.role == 'tenant':
            TenantProfile.objects.create(user=user)

        return user


class LoginSerializer(serializers.Serializer):
    # Simple serializer — just validates the incoming login credentials
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserSerializer(serializers.ModelSerializer):
    # Read-only serializer for returning user profile data
    # full_name comes from the @property we defined on the User model
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'phone_number',
            'role',
            'is_active',
            'is_verified',
            'date_joined',
        ]
        # These fields can never be changed through the API
        read_only_fields = ['id', 'date_joined', 'is_verified']


class LandlordProfileSerializer(serializers.ModelSerializer):
    # Read-only convenience fields pulled from the related User
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    phone_number = serializers.CharField(source='user.phone_number', read_only=True)

    class Meta:
        model = LandlordProfile
        fields = [
            'id',
            'full_name',
            'email',
            'phone_number',
            'profile_photo',
            'bio',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TenantProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    phone_number = serializers.CharField(source='user.phone_number', read_only=True)
    employment_status_display = None  # removed field — no longer applicable

    class Meta:
        model = TenantProfile
        fields = [
            'id',
            'full_name',
            'email',
            'phone_number',
            'national_id',
            'profile_photo',
            'occupation',
            'emergency_contact_name',
            'emergency_contact_phone',
            'emergency_contact_relationship',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_national_id(self, value):
        if not value:
            return value

        cleaned = value.strip()

        # Kenyan national IDs are numeric only, typically 7-8 digits
        if not cleaned.isdigit():
            raise serializers.ValidationError('National ID must contain numbers only.')

        if len(cleaned) not in (7, 8):
            raise serializers.ValidationError('National ID must be 7 or 8 digits long.')

        return cleaned

    def validate_emergency_contact_phone(self, value):
        if not value:
            return value

        cleaned = value.strip().replace(' ', '').replace('-', '')

        if cleaned.startswith('+'):
            cleaned = cleaned[1:]
        if cleaned.startswith('0'):
            cleaned = '254' + cleaned[1:]
        elif cleaned.startswith('7') or cleaned.startswith('1'):
            cleaned = '254' + cleaned

        if not cleaned.isdigit() or len(cleaned) != 12 or not cleaned.startswith('254'):
            raise serializers.ValidationError(
                'Enter a valid Kenyan phone number, e.g. 0712345678 or 254712345678.'
            )

        return cleaned
    
