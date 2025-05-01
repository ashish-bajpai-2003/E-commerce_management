# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.core.mail import send_mail
# from .models import Myproduct

# @receiver(post_save, sender=Myproduct)
# def send_stock_alert(sender, instance, **kwargs):
#     print("Signal triggered!")
#     print("Quantity:", instance.product_quantity)

#     # Check if quantity is zero
#     if instance.product_quantity == '0':
#         # Send email to seller
#         if instance.seller.email:
#             send_mail(
#                 'Stock Alert: Product Out of Stock',
#                 f'Hello {instance.seller.username}, your product "{instance.product_name}" is now out of stock.',
#                 'noreply@yourshop.com',
#                 [instance.seller.email],
#                 fail_silently=False,


#             )
#             print(f"Stock alert sent to seller: {instance.seller.email}")
#         else:
#             print("Seller email not found!")










# from .models import MyOrder  # also import Order
# from django.conf import settings

# @receiver(post_save, sender=MyOrder)
# def update_stock_and_notify(sender, instance, created, **kwargs):
#     if created:
#         product = instance.product
#         try:
#             current_qty = int(product.product_quantity)
#         except ValueError:
#             current_qty = 0

#         new_qty = current_qty - instance.quantity
#         product.product_quantity = str(max(new_qty, 0))
#         product.save()

#         if new_qty <= 0:
#             subject = f"'{Myproduct.product_name}' is out of stock"
#             message = (
#                 f"Hello {Myproduct.seller.username}, your product "
#                 f"\"{Myproduct.product_name}\" (ID {Myproduct.id}) is now out of stock."
#             )
#             send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
#                       [product.seller.email])

        


from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Myproduct
from django.core.mail import send_mail

@receiver(post_save, sender=Myproduct)
def check_stock_zero(sender, instance, **kwargs):
    if instance.stock == 0:
        send_mail(
            subject='Out of Stock Alert',
            message=f'Your product "{instance.product_name}" is now out of stock.',
            from_email='noreply@yourdomain.com',
            recipient_list=[instance.seller.email],
        )