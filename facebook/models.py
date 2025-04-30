from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from django.conf import settings

class CustomUser(AbstractUser):
    username = models.CharField(max_length=100,unique=True)
    USER_ROLES = (
        ('admin', 'Admin'),
        ('seller', 'Seller'),
        ('customer', 'Customer'),
    )
    user_type = models.CharField(max_length=10, choices=USER_ROLES)
    is_verified = models.BooleanField(default=False)  

   
    def __str__(self):
        return f"{self.username} ({self.user_type})"

class UserOTP(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.otp}"
    @property
    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=2)
    

class Category(models.Model):
    cname=models.CharField(max_length=200,null=True)
    cpic=models.ImageField(upload_to='static/category/',null=True, blank=True)
    cdate=models.DateField()
    def __str__(self):
        return  self.cname
    
class Subcategory(models.Model):
    category_name=models.ForeignKey(Category,on_delete=models.CASCADE)
    subcategory_name=models.CharField(max_length=100,null=True)
    def __str__(self):
        return self.subcategory_name
    

class Myproduct(models.Model):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product_category=models.ForeignKey(Category,on_delete=models.CASCADE,null=True,blank=True)
    subcategory_name=models.ForeignKey(Subcategory,on_delete=models.CASCADE,null=True,blank=True)
    product_name=models.CharField(max_length=200,null=True)
    price=models.IntegerField()
    discount_price=models.IntegerField(null=True, blank=True)
    product_pic=models.ImageField(upload_to='static/product/',null=True)
    total_discount=models.IntegerField(null=True, blank=True)
    product_quantity=models.CharField(max_length=200)
    pdate=models.DateField(default=timezone.now)


    def __str__(self):
        if self.product_category:
            return self.product_category.cname
        return 'No Category Assigned'



class cart(models.Model):
    userid=models.CharField(max_length=200,null=True)
    product_name=models.CharField(max_length=200)
    quantity=models.IntegerField(null=True)
    price=models.IntegerField(default=0)
    total_price=models.FloatField(default=0)
    product_picture=models.CharField(max_length=300,null=True)
    pw=models.CharField(max_length=200,null=True)
    added_date=models.DateField()

class MyOrder(models.Model):
    userid = models.CharField(max_length=200, null=True)
    product_name = models.CharField(max_length=200)
    quantity = models.IntegerField(null=True)
    price = models.IntegerField(null=True)
    total_price = models.FloatField(null=True)
    product_picture = models.CharField(max_length=300, null=True)
    pw = models.CharField(max_length=200, null=True)
    order_date = models.DateField(null=True)
    status=models.CharField(max_length=200,null=True)
    


