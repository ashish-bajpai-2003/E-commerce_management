from django import forms
from captcha.fields import CaptchaField
from .models import Category, Subcategory

class OTPForm(forms.Form):
    otp = forms.CharField(
        label="Enter OTP",
        max_length=6,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter 6-digit OTP'})
    )
    
class Myform(forms.Form):
    captcha=CaptchaField()


from django import forms
from .models import Myproduct

class ProductForm(forms.ModelForm):
    class Meta:
        model = Myproduct
        fields = ['product_name', 'price','discount_price', 'product_quantity', 'product_pic', 'product_category', 'subcategory_name']



from captcha.fields import CaptchaField

class Myform(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=[
        ('customer', 'Customer'),
        ('seller', 'Seller'),
        ('admin', 'Admin'),
    ])
    captcha = CaptchaField()


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['cname', 'cpic', 'cdate']



class SubcategoryForm(forms.ModelForm):
    class Meta:
        model = Subcategory
        fields = ['category_name', 'subcategory_name']


