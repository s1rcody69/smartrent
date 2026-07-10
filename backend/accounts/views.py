from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model

from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    LandlordProfileSerializer,
    TenantProfileSerializer,
)
from .models import LandlordProfile, TenantProfile

# Always use get_user_model() to reference the custom user model
User = get_user_model()


class RegisterView(APIView):
    # AllowAny — registration must be accessible without a token
    permission_classes = [AllowAny]

    def post(self, request):
        # Pass incoming request data into the serializer for validation
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            # Save the user — triggers the create() method in the serializer
            user = serializer.save()

            # Generate JWT tokens immediately after registration
            refresh = RefreshToken.for_user(user)

            return Response({
                'message': 'Account created successfully.',
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)

        # Return validation errors if serializer is invalid
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    # AllowAny — login must be accessible without a token
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email'].lower()
            password = serializer.validated_data['password']

            # authenticate() checks the credentials against the database
            # It returns None if credentials are invalid
            user = authenticate(request, username=email, password=password)

            if user is None:
                return Response(
                    {'error': 'Invalid email or password.'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            if not user.is_active:
                return Response(
                    {'error': 'This account has been deactivated.'},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Generate fresh tokens on every successful login
            refresh = RefreshToken.for_user(user)

            return Response({
                'message': 'Login successful.',
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    # IsAuthenticated — only logged-in users can logout
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Get the refresh token from the request body
            refresh_token = request.data.get('refresh')

            if not refresh_token:
                return Response(
                    {'error': 'Refresh token is required.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Blacklist the token — it can never be used again
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {'message': 'Logged out successfully.'},
                status=status.HTTP_200_OK
            )
        except Exception:
            return Response(
                {'error': 'Invalid token.'},
                status=status.HTTP_400_BAD_REQUEST
            )


class MeView(APIView):
    # IsAuthenticated — only logged-in users can view their own profile
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # request.user is automatically set by JWT authentication middleware
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LandlordProfileView(APIView):
    # Landlord views/updates their own profile only
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.landlord_profile
        except LandlordProfile.DoesNotExist:
            return Response(
                {'error': 'Landlord profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = LandlordProfileSerializer(profile)
        return Response(serializer.data)

    def patch(self, request):
        try:
            profile = request.user.landlord_profile
            user = request.user
        except LandlordProfile.DoesNotExist:
            return Response(
                {'error': 'Landlord profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Update User fields if provided
        user_data = {}
        if 'first_name' in request.data:
            user_data['first_name'] = request.data.pop('first_name')
        if 'last_name' in request.data:
            user_data['last_name'] = request.data.pop('last_name')
        if 'phone_number' in request.data:
            user_data['phone_number'] = request.data.pop('phone_number')
        
        if user_data:
            user_serializer = UserSerializer(user, data=user_data, partial=True)
            if user_serializer.is_valid():
                user_serializer.save()
        
        # Update profile fields
        serializer = LandlordProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # Refresh user data
            profile.refresh_from_db()
            return Response(LandlordProfileSerializer(profile).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TenantProfileView(APIView):
    # Tenant views/updates their own profile only
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.tenant_profile
        except TenantProfile.DoesNotExist:
            return Response(
                {'error': 'Tenant profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = TenantProfileSerializer(profile)
        return Response(serializer.data)

    def patch(self, request):
        try:
            profile = request.user.tenant_profile
            user = request.user
        except TenantProfile.DoesNotExist:
            return Response(
                {'error': 'Tenant profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Update User fields if provided
        user_data = {}
        if 'first_name' in request.data:
            user_data['first_name'] = request.data.pop('first_name')
        if 'last_name' in request.data:
            user_data['last_name'] = request.data.pop('last_name')
        if 'phone_number' in request.data:
            user_data['phone_number'] = request.data.pop('phone_number')
        
        if user_data:
            user_serializer = UserSerializer(user, data=user_data, partial=True)
            if user_serializer.is_valid():
                user_serializer.save()
        
        # Update profile fields
        serializer = TenantProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # Refresh user data
            profile.refresh_from_db()
            return Response(TenantProfileSerializer(profile).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AvailableTenantsListView(APIView):
    """List all tenants without active leases — only accessible to landlords and admins."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Only landlords and admins can see the tenant list
        if request.user.role not in ['landlord', 'admin']:
            return Response(
                {'error': 'You do not have permission to view tenants.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get all tenant profiles with user details
        tenants = TenantProfile.objects.select_related('user').all()
        
        # Filter out tenants with active leases
        from leases.models import Lease
        tenant_ids_with_active_leases = Lease.objects.filter(
            status='active'
        ).values_list('tenant_id', flat=True)
        
        available_tenants = tenants.exclude(id__in=tenant_ids_with_active_leases)
        
        serializer = TenantProfileSerializer(available_tenants, many=True)
        return Response(serializer.data)


class AdminUsersListView(APIView):
    """List all platform users — only accessible to admins."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Only admins can see all users
        if request.user.role != 'admin':
            return Response(
                {'error': 'You do not have permission to view all users.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get all users ordered by most recent first
        users = User.objects.all().order_by('-date_joined')
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)