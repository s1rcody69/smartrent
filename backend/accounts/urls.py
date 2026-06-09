from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, LoginView, LogoutView, MeView

# All URLs here are prefixed with /api/auth/ — set in the root urls.py
urlpatterns = [
    # Registration endpoint
    path('register/', RegisterView.as_view(), name='auth-register'),

    # Login endpoint
    path('login/', LoginView.as_view(), name='auth-login'),

    # Logout endpoint — blacklists the refresh token
    path('logout/', LogoutView.as_view(), name='auth-logout'),

    # Token refresh endpoint — provided by SimpleJWT
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    # Current user profile endpoint
    path('me/', MeView.as_view(), name='auth-me'),
]