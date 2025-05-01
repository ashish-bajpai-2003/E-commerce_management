from django.shortcuts import render,HttpResponse,HttpResponseRedirect,redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.shortcuts import  redirect
import random
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from .models import CustomUser,UserOTP
from django.db.models import Q
from .forms import Myform ,OTPForm, CategoryForm
from .models import Subcategory,Myproduct,Category, cart, MyOrder
from.task import send_seller_status_email
from .forms import CategoryForm, SubcategoryForm
from django.utils import timezone
from datetime import datetime

def home(request):
    data = Category.objects.all().order_by('-id')
    md = {
        "cdata": data,
        # "form": form,
        # "is_seller": is_seller
    }
    return render(request, 'home.html', md)


def category_edit(request, category_id):
    if not request.user.is_authenticated or request.user.user_type != 'seller':
        messages.error(request, "You are not authorized to edit categories.")
        return redirect('home')
    category = get_object_or_404(Category, pk=category_id)

    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = CategoryForm(instance=category)

    return render(request, 'category_edit.html', {'form': form})

# Delete Category
def category_delete(request, category_id):
    if not request.user.is_authenticated or request.user.user_type != 'seller':
        messages.error(request, "You are not authorized to delete categories.")
        return redirect('home')
    category = get_object_or_404(Category, pk=category_id)
    category.delete()
    return redirect('home')

def about(request):
    return render(request,'aboutus.html')

def generate_otp():
    return str(random.randint(100000, 999999))



def verify_otp(request):
    temp_user_data = request.session.get('temp_user_data')
    if not temp_user_data:
        return redirect('register_user')

    form = OTPForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            entered_otp = form.cleaned_data['otp']
            real_otp = request.session.get('otp')

            if real_otp and entered_otp == real_otp:
                # Create the user now
                user = CustomUser.objects.create_user(
                    username=temp_user_data['username'],
                    email=temp_user_data['email'],
                    password=temp_user_data['password'],
                    user_type='customer',
                    is_verified=True
                )

                # Clear session data
                del request.session['temp_user_data']
                del request.session['otp']

                messages.success(request, "OTP Verified! You can now log in.")
                return redirect('login')
            else:
                messages.error(request, "Invalid OTP. Please try again.")

    if request.method == "GET" and 'resend_otp' in request.GET:
        otp = generate_otp()
        request.session['otp'] = otp
        send_mail(
            subject='Resent OTP for Account Verification',
            message=f'Your new OTP is {otp}',
            from_email='your_email@gmail.com',
            recipient_list=[temp_user_data['email']],
        )
        messages.success(request, "New OTP sent to your email.")
        return redirect('verify_otp')

    return render(request, 'verify_otp.html', {'form': form})


def register_user(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        role = request.POST['role']

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register_user')

        if role == 'customer':
            otp = generate_otp()

            # Save user data in session temporarily
            request.session['temp_user_data'] = {
                'username': username,
                'email': email,
                'password': password,
                'role': role
            }
            request.session['otp'] = otp

            send_mail(
                subject='Your OTP for Account Verification',
                message=f'Your OTP is {otp}',
                from_email='your_email@gmail.com',
                recipient_list=[email],
            )

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


        if not user.is_verified:
            request.session['username'] = user.username 
            messages.error(request, "Please verify your OTP before logging in.")
            return redirect('verify_otp')

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
    products = Myproduct.objects.all()
    return render(request, 'admin_dashboard.html',{'sellers': sellers,'customers': customers,'products' : products})

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


def delete_product(request, pid):
    product = get_object_or_404(Myproduct, id=pid)
    if request.method == 'POST':
        product.delete()
        return redirect('admin_dashboard')
    return redirect('admin_dashboard')



def user_logout(request):
    logout(request)
    return redirect('login')


from .models import Subcategory,Myproduct

def product(request):
    catid=request.GET.get('cid')
    subcatid=request.GET.get('sid')


    if catid:
        sdata=Subcategory.objects.filter(category_name=catid).order_by('-id')
    else:
        sdata = Subcategory.objects.all().order_by('-id')
    if subcatid is not None:
        pdata=Myproduct.objects.all().filter(subcategory_name=subcatid)
    elif catid is not None:
        pdata=Myproduct.objects.all().filter(product_category=catid)
    else :
        pdata=Myproduct.objects.all().order_by('-id')
    md={"subcat":sdata,"pdata":pdata}
    return render(request,'product.html',md)








from django.shortcuts import render, redirect, get_object_or_404
from .models import  Myproduct
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

    products = Myproduct.objects.filter(seller=seller)
    return render(request, 'seller_dashboard.html', {'form': form, 'products': products})

def product_update(request, pk):
    if not request.user.is_authenticated:
        return redirect('login')

    product = get_object_or_404(Myproduct, pk=pk, seller=request.user)

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

    product = get_object_or_404(Myproduct, pk=pk, seller=request.user)
    product.delete()
    return redirect('seller_dashboard')

from datetime import datetime

def mycart(request):
    if request.method == "GET":
        pname = request.GET.get("pname")
        price = request.GET.get("price")
        discount_price = request.GET.get("discount_price")
        ppic = request.GET.get("ppic")
        pw = request.GET.get("pw")
        qt = request.GET.get("qt")

        print("Pname from GET:", pname)
        product = Myproduct.objects.get(product_name=pname)
        stock = int(product.product_quantity)
       

        if int(qt) > product.stock:
            return HttpResponse(f"<script>alert('Only {stock} item(s) in stock'); location.href='/product/';</script>")

        if int(qt) <= 0:
            return HttpResponse("<script>alert('Add a valid product quantity'); location.href='/product/';</script>")

        if not (pname and price and discount_price and ppic and pw):
            return redirect('showcart') 

        qt = int(qt)
        total_price = float(discount_price) * qt

        cart = request.session.get('cart', [])
        item = {
            'cart_id': pw,
            'pname': pname,
            'price': price,
            'discount_price': discount_price,
            'ppic': ppic,
            'qt': qt,
            'total_price': total_price,
            'added_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        cart.append(item)
        request.session['cart'] = cart
        request.session.modified = True

        product.product_quantity = str(stock - qt)
        product.save()

        return redirect('showcart')

    elif request.method == "POST":
        cart = request.session.get('cart', [])
        for item in cart:
            cart_id = item.get('cart_id')
            new_quantity = request.POST.get(f'qt_{cart_id}')
            if new_quantity and new_quantity.isdigit() and int(new_quantity) > 0:
                new_quantity = int(new_quantity)
                item['qt'] = new_quantity
                item['total_price'] = new_quantity * float(item['discount_price'])
        request.session['cart'] = cart
        request.session.modified = True
        return redirect('showcart')

    else:
        cart = request.session.get('cart', [])
        total_price = sum(item['total_price'] for item in cart)
        return render(request, 'cart.html', {'cart': cart, 'total_price': total_price})
    

def update_quantity(request, cart_id):
 
    new_qty = request.GET.get("quantity")
    
  
    if new_qty and new_qty.isdigit() and int(new_qty) > 0:
        new_qty = int(new_qty)
    else:
        return redirect('showcart')

    cart = request.session.get('cart', [])
    
    for item in cart:
        if item['cart_id'] == cart_id:
            item['qt'] = new_qty
            item['total_price'] = float(item['discount_price']) * new_qty
            break

    request.session['cart'] = cart
    request.session.modified = True
    return redirect('showcart') 


def remove_from_cart(request, cart_id):
    cart = request.session.get('cart', [])
    
    cart = [item for item in cart if item['cart_id'] != cart_id]
    
    request.session['cart'] = cart
    request.session.modified = True
    return redirect('showcart') 


def showcart(request):
    cart = request.session.get('cart', [])
    total_price = 0
    updated_cart = []

    if request.method == 'POST':
        updated_cart_items = request.POST.getlist('qt')
        for i, item in enumerate(cart):
            if updated_cart_items[i].isdigit() and int(updated_cart_items[i]) > 0:
                item['qt'] = int(updated_cart_items[i])  # Update quantity
                item['subtotal'] = float(item['discount_price']) * item['qt']
            total_price += item['subtotal']
        
        request.session['cart'] = cart
        request.session.modified = True
        return redirect('showcart')  # Redirect to show updated cart

    for item in cart:
        try:
            item['subtotal'] = float(item['discount_price']) * int(item['qt'])
            total_price += item['subtotal']
        except (ValueError, TypeError):
            continue
        updated_cart.append(item)

    return render(request, 'cart.html', {'cart': updated_cart, 'total_price': total_price})

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
    products = Myproduct.objects.none()

    if query:
        products = Myproduct.objects.filter(
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
    orders = MyOrder.objects.filter(userid=request.user).order_by('-order_date')

    print(f"Orders: {orders}")

    return render(request, 'myorders.html', {'orders': orders})




@login_required
def user_cart_products(request):
    user_cart_items = cart.objects.filter(userid=request.user.username)
    return render(request, 'user_cart_products.html', {'cart_items': user_cart_items})



def subcategory_view(request, cid):
    subcategories = Subcategory.objects.filter(category_id=cid)
    return render(request, 'subcategory.html', {'subcategories': subcategories})


def place_order(request, product_name):
    if request.method == 'GET':
        quantity = request.GET.get('qt')
        price = request.GET.get('price')

        if quantity and price:
            quantity = int(quantity)
            price = float(price)

            product = get_object_or_404(Myproduct, product_name=product_name)

            order = MyOrder.objects.create(
                userid=request.user,
                product=product,
                product_name=product.product_name,
                quantity=quantity,
                price=price,
                total_price=quantity * price,
                product_picture=product.product_pic.url if product.product_pic else '',
                pw=product.id,
                order_date=timezone.now(),
                status='Pending',
            )

         
            print(f"Order Created: {order}")
            product.stock -= quantity  
            product.save() 

            cart = request.session.get('cart', [])
            cart = [item for item in cart if item['pname'] != product_name]
            request.session['cart'] = cart
            request.session.modified = True

            return redirect('myorders')
    return redirect('showcart')


@login_required
def add_category(request):
    form = CategoryForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('add_category')
    return render(request, 'add_category.html', {'form': form})

@login_required
def add_subcategory(request):
    form = SubcategoryForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('add_subcategory')
    return render(request, 'add_subcategory.html', {'form': form})