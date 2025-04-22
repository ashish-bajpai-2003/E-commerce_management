# signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import myproduct

@receiver(post_save, sender=myproduct)
def send_stock_alert(sender, instance, **kwargs):
    if instance.product_quantity == 0:
        send_mail(
            'Stock Alert: Product Out of Stock',
            f'Your product "{instance.veg_name}" is now out of stock.',
            'noreply@yourshop.com',
            [instance.product_category.email],
            fail_silently=False,
        )