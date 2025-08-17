from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CustomTokenObtainPairView, RegisterView, VerifyEmailView,
    UserProfileView, UserProfileDetailView, ChangePasswordView,
    ForgotPasswordView, ResetPasswordView, FollowerListView,
    FollowerDetailView, UserActivityListView
)

urlpatterns = [
    # Authentication
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-email/<str:uidb64>/<str:token>/', VerifyEmailView.as_view(), name='verify_email'),
    
    # Password management
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/<str:uidb64>/<str:token>/', ResetPasswordView.as_view(), name='reset_password'),
    
    # User profile
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('profile/<int:pk>/', UserProfileDetailView.as_view(), name='user_profile_detail'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    
    # Followers
    path('users/<int:user_id>/followers/', FollowerListView.as_view(), name='user_followers'),
    path('users/<int:user_id>/follow/', FollowerListView.as_view(), name='follow_user'),
    path('users/<int:user_id>/unfollow/', FollowerDetailView.as_view(), name='unfollow_user'),
    
    # User activities
    path('users/<int:user_id>/activities/', UserActivityListView.as_view(), name='user_activities'),
    
    # JWT token refresh
    path('token/refresh/', CustomTokenObtainPairView.as_view(), name='token_refresh'),
]