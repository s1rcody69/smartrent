from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import LandlordProfile, TenantProfile

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
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
            'date_joined',
        ]
        read_only_fields = ['id', 'is_active', 'date_joined']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        label="Confirm Password"
    )
    role = serializers.ChoiceField(
        choices=['landlord', 'tenant'],
        required=True
    )
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = [
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'password',
            'password2',
            'role',
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                'password2': 'Passwords do not match.'
            })
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        role = validated_data.pop('role')

        user = User.objects.create_user(**validated_data)
        user.role = role
        user.save()

        if role == 'landlord':
            LandlordProfile.objects.create(user=user)
        elif role == 'tenant':
            TenantProfile.objects.create(user=user)

        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class LandlordProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(source='user.id', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    phone_number = serializers.CharField(source='user.phone_number', read_only=True)

    class Meta:
        model = LandlordProfile
        fields = [
            'id',
            'user_id',
            'email',
            'full_name',
            'first_name',
            'last_name',
            'phone_number',
            'bio',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TenantProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(source='user.id', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    phone_number = serializers.CharField(source='user.phone_number', read_only=True)

    class Meta:
        model = TenantProfile
        fields = [
            'id',
            'user_id',
            'email',
            'full_name',
            'first_name',
            'last_name',
            'phone_number',
            'national_id',
            'occupation',
            'emergency_contact_name',
            'emergency_contact_phone',
            'emergency_contact_relationship',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
