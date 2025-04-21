from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
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
    

class Category(models.Model):
    cname=models.CharField(max_length=200,null=True)
    cpic=models.ImageField(upload_to='static/category/',null=True)
    cdate=models.DateField()
    def __str__(self):
        return  self.cname
    
class subcategory(models.Model):
    category_name=models.ForeignKey(Category,on_delete=models.CASCADE)
    subcategory_name=models.CharField(max_length=100,null=True)

    def __str__(self):
        return self.subcategory_name
    

class myproduct(models.Model):
    product_category=models.ForeignKey(Category,on_delete=models.CASCADE)
    subcategory_name=models.ForeignKey(subcategory,on_delete=models.CASCADE)
    veg_name=models.CharField(max_length=200,null=True)
    price=models.IntegerField()
    discount_price=models.IntegerField()
    product_pic=models.ImageField(upload_to='static/product/',null=True)
    total_discount=models.IntegerField()
    product_quantity=models.CharField(max_length=200)
    pdate=models.DateField()