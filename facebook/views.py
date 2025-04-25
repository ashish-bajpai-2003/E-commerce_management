from django.shortcuts import render,HttpResponse,HttpResponseRedirect,redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.shortcuts import  redirect
import random
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from .models import CustomUser,UserOTP
from django.db.models import Q
from .forms import Myform ,OTPForm
from .models import subcategory,myproduct,Category, cart
from.task import send_seller_status_email
def home(request):
    data=Category.objects.all().order_by('-id')
    md={"cdata":data}
    return render(request, 'home.html',md)

def about(request):
    return render(request,'aboutus.html')

def generate_otp():
    return str(random.randint(100000, 999999))



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
                if real_otp:
                    if real_otp.is_expired:
                        messages.error(request, "OTP has expired. Please request a new one.")
                    elif entered_otp == real_otp.otp:
                        user.is_active = True
                        user.save()
                        real_otp.delete()
                        messages.success(request, "Otp Verified.")
 
                        return redirect('login')
                    else:
                        messages.error(request, "Invalid OTP. Please try again.")
    
    if request.method == "GET" and 'resend_otp' in request.GET:
        user = CustomUser.objects.filter(username=username).first()
        if user:
            otp = generate_otp()
            UserOTP.objects.update_or_create(user=user, defaults={'otp': otp})
            send_mail(
                "Your OTP Code",
                f"Your OTP code is {otp}",
                'from@example.com', 
                [user.email],
                fail_silently=False,
            )
            messages.success(request, "A new OTP has been sent to your email.")
        return redirect('verify_otp')  

    return render(request, 'verify_otp.html', {'form': form})
# 

def register_user(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        role = request.POST['role']

        if role == 'customer':
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

        elif role == 'seller':
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                user_type='seller',
                is_verified=False 
            )
            return HttpResponse("Seller registered successfully. Please wait for admin verification.")

        elif role == 'admin':
            user = CustomUser.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                user_type='admin',
                is_verified=True
            )
            return redirect('login')

        else:
            messages.error(request, "Invalid role selected.")
            return redirect('register_user')

    return render(request, 'register_user.html')


def user_login(request):
    form = Myform(request.POST or None)

    if request.method == "POST" and form.is_valid():
        uname = form.cleaned_data['username']
        pwd   = form.cleaned_data['password']
        role  = form.cleaned_data['role']

        qs = CustomUser.objects.filter(username=uname, user_type=role)

        if not qs.exists():
            messages.error(request, "Invalid username or role.")
            return render(request, 'login.html', {'form': form})

        user = None
        for u in qs:
            if u.check_password(pwd):
                user = u
                break

        if not user:
            messages.error(request, "Incorrect password.")
            return render(request, 'login.html', {'form': form})

        if role == 'seller' and not user.is_verified:
            messages.error(request, "Seller account not verified yet. Please wait.")
            return render(request, 'login.html', {'form': form})

        login(request, user)
        if role == 'seller':
            return redirect('seller_dashboard')
        elif role == 'customer':
            return redirect('customer_dashboard')
        else:
            return redirect('admin_dashboard')

    return render(request, 'login.html', {'form': form})


@login_required
def seller_dashboard(request):
    return render(request, 'seller_dashboard.html')

@login_required
def customer_dashboard(request):
    return render(request, 'customer_dashboard.html')

@login_required
def admin_dashboard(request):
    sellers = CustomUser.objects.filter(user_type='seller')
    customers = CustomUser.objects.filter(user_type='customer')
    return render(request, 'admin_dashboard.html',{'sellers': sellers,'customers': customers})

@login_required
def approve_seller(request, seller_id):
    if request.user.user_type != 'admin':
        return HttpResponse("Unauthorized access.")

    seller = get_object_or_404(CustomUser, id=seller_id, user_type='seller')
    seller.is_verified = True
    seller.save()
    send_seller_status_email.delay(seller.email, 'approved')
    return redirect('admin_dashboard') 

@login_required
def unapprove_seller(request, seller_id):
    if request.user.user_type != 'admin':
        return HttpResponse("Unauthorized access.")
    
    seller = get_object_or_404(CustomUser, id=seller_id, user_type='seller')
    seller.is_verified = False
    seller.save()
    send_seller_status_email.delay(seller.email, 'unapproved')
    return redirect('admin_dashboard') 

@login_required
def delete_seller(request, seller_id):
    if request.user.user_type != 'admin':
        return HttpResponse("Unauthorized access.")
    
    seller = get_object_or_404(CustomUser, id=seller_id, user_type='seller')
    seller.delete()
    return redirect('admin_dashboard') 

@login_required
def delete_customer(request, customer_id):
    if request.user.user_type != 'admin':
        return HttpResponse("Unauthorized access.")

    customer = get_object_or_404(CustomUser, id=customer_id, user_type='customer')
    customer.delete()
    return redirect('admin_dashboard')







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


def mycartu(request):
    user=request.objects.get('user')
    return render(request,'mycart.html',{'user':user})







from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, myproduct
from .forms import ProductForm

def seller_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')

    seller = request.user
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = seller
            product.save()
            return redirect('seller_dashboard')
    else:
        form = ProductForm()

    products = myproduct.objects.filter(seller=seller)
    return render(request, 'seller_dashboard.html', {'form': form, 'products': products})

def product_update(request, pk):
    if not request.user.is_authenticated:
        return redirect('login')

    product = get_object_or_404(myproduct, pk=pk, seller=request.user)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('seller_dashboard')
    else:
        form = ProductForm(instance=product)

    return render(request, 'product_add.html', {'form': form})

def product_delete(request, pk):
    if not request.user.is_authenticated:
        return redirect('login')

    product = get_object_or_404(myproduct, pk=pk, seller=request.user)
    product.delete()
    return redirect('seller_dashboard')


def mycart(request):
    if request.method == "GET":
        cname = request.GET.get("cname")
        pname = request.GET.get("pname")
        price = request.GET.get("price")
        discount_price = request.GET.get("discount_price")
        ppic = request.GET.get("ppic")
        pw = request.GET.get("pw")
        qt = request.GET.get("qt")

        
        if qt and qt.isdigit() and int(qt) > 0:
            qt = int(qt)  
        else:
            qt = 1  

        cart = request.session.get('cart', [])
        item = {
            'pname': pname,
            'price': price,
            'discount_price': discount_price,
            'ppic': ppic,
            'pw': pw,
            'qt': qt,
        }
        cart.append(item)
        request.session['cart'] = cart
        request.session.modified = True

        return redirect('showcart')



def showcart(request):
    cart = request.session.get('cart', [])
    return render(request, 'cart.html', {'cart': cart})





def product_add(request):
    if not request.user.is_authenticated:
        return redirect('login') 

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user 
            product.save()
            return redirect('seller_dashboard')
    else:
        form = ProductForm()

    return render(request, 'product_add.html', {'form': form})



def product_search(request):
    query = request.GET.get('q','').strip()
    products = myproduct.objects.none()

    if query:
        products = myproduct.objects.filter(
            Q(product_name__icontains=query) |
            Q(product_category__cname__icontains=query) |
            Q(subcategory_name__subcategory_name__icontains=query)
        ).distinct()

    return render(request, 'product_search.html', {
        'products': products,
        'query': query
    })

@login_required
def myorders(request):
    # agar order model bana hai, fetch karo, varna session-based orders dikhao
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'myorders.html', {'orders': orders})





@login_required
def user_cart_products(request):
    user_cart_items = cart.objects.filter(userid=request.user.username)
    return render(request, 'user_cart_products.html', {'cart_items': user_cart_items})