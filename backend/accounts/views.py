from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import UserProfile, Follower, UserActivity
from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    UserProfileUpdateSerializer, ChangePasswordSerializer,
    FollowerSerializer, UserActivitySerializer
)
from .permissions import IsOwnerOrReadOnly

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT token view that uses email instead of username"""
    
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response(
                {'error': 'Email and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(request, username=email, password=password)
        
        if user is None:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not user.is_active:
            return Response(
                {'error': 'Account is disabled'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        })


class RegisterView(generics.CreateAPIView):
    """User registration view"""
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Send verification email
        self.send_verification_email(user)
        
        # Log user activity
        UserActivity.objects.create(
            user=user,
            activity_type='profile_updated',
            description=f"User {user.email} registered successfully"
        )
        
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Registration successful. Please check your email for verification.',
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    
    def send_verification_email(self, user):
        """Send email verification link"""
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        verification_url = f"{settings.FRONTEND_URL}/verify-email/{uid}/{token}/"
        
        subject = 'Verify your email address'
        message = f"""
        Hi {user.first_name},
        
        Please verify your email address by clicking the link below:
        {verification_url}
        
        This link will expire in 24 hours.
        
        If you didn't create this account, please ignore this email.
        
        Best regards,
        The AmaderFoodie Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )


class VerifyEmailView(generics.GenericAPIView):
    """Email verification view"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        
        if user is not None and default_token_generator.check_token(user, token):
            user.is_verified = True
            user.save()
            
            # Log user activity
            UserActivity.objects.create(
                user=user,
                activity_type='profile_updated',
                description=f"User {user.email} verified email address"
            )
            
            return Response({'message': 'Email verified successfully'}, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'Invalid verification link'},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """User profile view for retrieving and updating user profile"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Log user activity
        UserActivity.objects.create(
            user=instance,
            activity_type='profile_updated',
            description=f"User {instance.email} updated profile"
        )
        
        return Response(serializer.data)


class UserProfileDetailView(generics.RetrieveAPIView):
    """Public user profile view"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'pk'


class ChangePasswordView(generics.GenericAPIView):
    """Change password view"""
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        # Log user activity
        UserActivity.objects.create(
            user=user,
            activity_type='profile_updated',
            description=f"User {user.email} changed password"
        )
        
        return Response({'message': 'Password changed successfully'})


class ForgotPasswordView(generics.GenericAPIView):
    """Forgot password view"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'error': 'User with this email does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Generate password reset token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
        
        # Send reset email
        subject = 'Reset your password'
        message = f"""
        Hi {user.first_name},
        
        You requested a password reset. Click the link below to reset your password:
        {reset_url}
        
        This link will expire in 24 hours.
        
        If you didn't request this reset, please ignore this email.
        
        Best regards,
        The AmaderFoodie Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        
        return Response({'message': 'Password reset email sent'})


class ResetPasswordView(generics.GenericAPIView):
    """Reset password view"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        
        if user is not None and default_token_generator.check_token(user, token):
            password = request.data.get('password')
            password_confirm = request.data.get('password_confirm')
            
            if not password or password != password_confirm:
                return Response(
                    {'error': 'Passwords do not match'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user.set_password(password)
            user.save()
            
            # Log user activity
            UserActivity.objects.create(
                user=user,
                activity_type='profile_updated',
                description=f"User {user.email} reset password"
            )
            
            return Response({'message': 'Password reset successfully'})
        else:
            return Response(
                {'error': 'Invalid reset link'},
                status=status.HTTP_400_BAD_REQUEST
            )


class FollowerListView(generics.ListCreateAPIView):
    """List and create followers"""
    serializer_class = FollowerSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        return Follower.objects.filter(following_id=user_id)
    
    def perform_create(self, serializer):
        following_id = self.kwargs.get('user_id')
        following = User.objects.get(id=following_id)
        
        if following == self.request.user:
            raise serializers.ValidationError("You cannot follow yourself")
        
        if Follower.objects.filter(follower=self.request.user, following=following).exists():
            raise serializers.ValidationError("You are already following this user")
        
        serializer.save(follower=self.request.user, following=following)
        
        # Log user activity
        UserActivity.objects.create(
            user=self.request.user,
            activity_type='user_followed',
            description=f"User {self.request.user.email} followed {following.email}"
        )


class FollowerDetailView(generics.DestroyAPIView):
    """Unfollow user"""
    serializer_class = FollowerSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_object(self):
        following_id = self.kwargs.get('user_id')
        try:
            return Follower.objects.get(follower=self.request.user, following_id=following_id)
        except Follower.DoesNotExist:
            raise serializers.ValidationError("You are not following this user")
    
    def perform_destroy(self, instance):
        # Log user activity
        UserActivity.objects.create(
            user=self.request.user,
            activity_type='user_unfollowed',
            description=f"User {self.request.user.email} unfollowed {instance.following.email}"
        )
        
        super().perform_destroy(instance)


class UserActivityListView(generics.ListAPIView):
    """List user activities"""
    serializer_class = UserActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        return UserActivity.objects.filter(user_id=user_id)