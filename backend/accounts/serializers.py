from rest_framework import serializers
from django.contrib.auth import get_user_model

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
    
