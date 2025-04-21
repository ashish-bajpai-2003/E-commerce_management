from django.shortcuts import render,HttpResponse,HttpResponseRedirect,redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.shortcuts import  redirect
import random
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from .models import CustomUser,UserOTP
from .forms import Myform ,OTPForm
from .models import subcategory,myproduct,Category
from.task import send_seller_status_email
def home(request):
    data=Category.objects.all().order_by('-id')
    md={"cdata":data}
    return render(request, 'home.html',md)

def generate_otp():
    return str(random.randint(100000, 999999))

def register_customer(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            user_type='customer',
            is_verified=True  
        )
        otp = generate_otp()
        UserOTP.objects.create(user=user, otp=otp)
        send_mail(
                subject='Your OTP for Account Verification',
                message=f'Your OTP is {otp}',
                from_email='your_email@gmail.com',
                recipient_list=[user.email],
            )
        request.session['username'] = user.username  
        messages.success(request, "OTP sent to your email.")
        return redirect('verify_otp')
        # return redirect('login')
    return render(request, 'register_customer.html')

def verify_otp(request):
    username = request.session.get('username')
    if not username:
        return redirect('signup')

    form = OTPForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            entered_otp = form.cleaned_data['otp']
            user = CustomUser.objects.filter(username=username).first()
            if user:
                real_otp = UserOTP.objects.filter(user=user).first()
                if real_otp and entered_otp == real_otp.otp:
                    user.is_active = True
                    user.save()
                    real_otp.delete()
                    messages.success(request, "OTP verified! You can now login.")
                    return redirect('login')
                else:
                    messages.error(request, "Invalid OTP. Please try again.")

    return render(request, 'verify_otp.html', {'form': form})

def register_seller(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            user_type='seller',
            is_verified=False
        )
        messages.success(request,"Seller registered successfully. Please wait for admin verification.")
    return render(request, 'register_seller.html')


def register_admin(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        user = CustomUser.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            user_type='admin',
            is_verified=True  
        )
        return redirect('login')
    return render(request, 'register_admin.html')



def user_login(request):
    form = Myform(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.user_type == 'seller':
                    if not user.is_verified:
                        messages.success(request,"Seller account not verified by admin yet.")
                    else:
                        login(request, user)
                        return redirect('dashboard')
                elif user.user_type in ['admin', 'customer']:
                    login(request, user)
                    return redirect('dashboard')
            else:
                return render(request, 'login.html', {'form': form, 'error': 'Invalid credentials'})
        else:
            return render(request, 'login.html', {'form': form, 'error': 'Invalid captcha'})
    return render(request, 'login.html', {'form': form})


@login_required
def dashboard(request):
    user = request.user
    if user.user_type == 'admin':
        sellers = CustomUser.objects.filter(user_type='seller')
        return render(request, 'admin_dashboard.html', {'sellers':sellers})
    elif user.user_type == 'seller':
        return render(request, 'seller_dashboard.html')
    elif user.user_type == 'customer':
        return render(request, 'customer_dashboard.html')
    else:
        return HttpResponse("Unknown user type.")


@login_required
def approve_seller(request, seller_id):
    if request.user.user_type != 'admin':
        return HttpResponse("Unauthorized access.")

    seller = get_object_or_404(CustomUser, id=seller_id, user_type='seller')
    seller.is_verified = True
    seller.save()
    send_seller_status_email.delay(seller.email,'approved')
    return redirect('dashboard')

@login_required
def unapprove_seller(request, seller_id):
    if request.user.user_type != 'admin':
        return HttpResponse("Unauthorized access.")

    seller = get_object_or_404(CustomUser, id=seller_id, user_type='seller')
    seller.is_verified = False
    seller.save()
    send_seller_status_email.delay(seller.email,'Unapproved')
    return redirect('dashboard')



def user_logout(request):
    logout(request)
    return redirect('login')


from .models import subcategory,myproduct

def product(request):
    catid=request.GET.get('cid')
    subcatid=request.GET.get('sid')
    sdata=subcategory.objects.all().order_by('-id')
    if subcatid is not None:
        pdata=myproduct.objects.all().filter(subcategory_name=subcatid)
    elif catid is not None:
        pdata=myproduct.objects.all().filter(product_category=catid)
    else :
        pdata=myproduct.objects.all().order_by('-id')
    md={"subcat":sdata,"pdata":pdata}
    return render(request,'product.html',md)
