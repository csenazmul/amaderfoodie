from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import UserProfile, Follower, UserActivity

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        exclude = ('user',)


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    followers_count = serializers.IntegerField(read_only=True)
    following_count = serializers.IntegerField(read_only=True)
    recipes_count = serializers.IntegerField(read_only=True)
    blogs_count = serializers.IntegerField(read_only=True)
    profile_image_url = serializers.SerializerMethodField()
    cover_image_url = serializers.SerializerMethodField()
    specialties_list = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name', 'bio', 'location', 'phone',
            'profile_image', 'cover_image', 'profile_image_url', 'cover_image_url',
            'website', 'facebook', 'twitter', 'instagram', 'linkedin',
            'is_chef', 'chef_experience', 'specialties', 'specialties_list',
            'email_notifications', 'marketing_emails',
            'followers_count', 'following_count', 'recipes_count', 'blogs_count',
            'is_verified', 'is_premium', 'date_joined', 'last_login', 'profile'
        ]
        read_only_fields = [
            'id', 'email', 'is_verified', 'is_premium', 'date_joined', 'last_login',
            'followers_count', 'following_count', 'recipes_count', 'blogs_count'
        ]
    
    def get_profile_image_url(self, obj):
        return obj.get_profile_image_url()
    
    def get_cover_image_url(self, obj):
        return obj.get_cover_image_url()
    
    def get_specialties_list(self, obj):
        return obj.get_specialties_list()


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'password', 'password_confirm',
            'bio', 'location', 'phone'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        UserProfile.objects.create(user=user)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'bio', 'location', 'phone', 'website',
            'facebook', 'twitter', 'instagram', 'linkedin',
            'is_chef', 'chef_experience', 'specialties',
            'email_notifications', 'marketing_emails'
        ]
    
    def update(self, instance, validated_data):
        # Update specialties as a comma-separated string
        if 'specialties' in validated_data and isinstance(validated_data['specialties'], list):
            validated_data['specialties'] = ', '.join(validated_data['specialties'])
        
        return super().update(instance, validated_data)


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        exclude = ('user', 'created_at', 'updated_at')


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value


class FollowerSerializer(serializers.ModelSerializer):
    follower = UserSerializer(read_only=True)
    following = UserSerializer(read_only=True)
    
    class Meta:
        model = Follower
        fields = ['id', 'follower', 'following', 'created_at']
        read_only_fields = ['created_at']


class UserActivitySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserActivity
        fields = ['id', 'user', 'activity_type', 'description', 'related_object_id', 'related_object_type', 'created_at']
        read_only_fields = ['created_at']