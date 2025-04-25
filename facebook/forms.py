from django import forms
from captcha.fields import CaptchaField

class OTPForm(forms.Form):
    otp = forms.CharField(
        label="Enter OTP",
        max_length=6,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter 6-digit OTP'})
    )
    
class Myform(forms.Form):
    captcha=CaptchaField()


from django import forms
from .models import myproduct

class ProductForm(forms.ModelForm):
    class Meta:
        model = myproduct
        fields = ['product_name', 'price','discount_price', 'product_quantity', 'product_pic']



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



