from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserProfile, Cart

@receiver(post_save, sender=UserProfile)
def create_user_cart(sender, instance, created, **kwargs):
    if created and not hasattr(instance, 'cart'):
        Cart.objects.create(user_profile=instance)