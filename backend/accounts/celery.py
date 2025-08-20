from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import UserActivity

User = get_user_model()


@shared_task
def send_welcome_email(user_id):
    """Send welcome email to new user"""
    try:
        user = User.objects.get(id=user_id)
        subject = 'Welcome to AmaderFoodie!'
        message = f"""
        Hi {user.first_name},
        
        Welcome to AmaderFoodie! We're excited to have you join our community of food lovers.
        
        Here are some things you can do:
        - Share your favorite recipes
        - Write blog posts about your culinary experiences
        - Connect with other food enthusiasts
        - Discover new recipes and cooking techniques
        
        If you have any questions, feel free to reach out to our support team.
        
        Happy cooking!
        
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
        
        return f"Welcome email sent to {user.email}"
    except User.DoesNotExist:
        return f"User with ID {user_id} not found"
    except Exception as e:
        return f"Error sending welcome email: {str(e)}"


@shared_task
def send_notification_email(user_id, subject, message):
    """Send notification email to user"""
    try:
        user = User.objects.get(id=user_id)
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        
        return f"Notification email sent to {user.email}"
    except User.DoesNotExist:
        return f"User with ID {user_id} not found"
    except Exception as e:
        return f"Error sending notification email: {str(e)}"


@shared_task
def cleanup_old_activities():
    """Clean up old user activities (older than 90 days)"""
    from django.utils import timezone
    from datetime import timedelta
    
    cutoff_date = timezone.now() - timedelta(days=90)
    deleted_count = UserActivity.objects.filter(created_at__lt=cutoff_date).delete()[0]
    
    return f"Deleted {deleted_count} old activities"


@shared_task
def update_user_stats():
    """Update user statistics"""
    from django.db.models import Count, F
    
    # Update recipes count for all users
    User.objects.annotate(
        recipes_count=Count('recipes')
    ).update(recipes_count=F('recipes_count'))
    
    # Update blogs count for all users
    User.objects.annotate(
        blogs_count=Count('blogs')
    ).update(blogs_count=F('blogs_count'))
    
    return "User statistics updated"