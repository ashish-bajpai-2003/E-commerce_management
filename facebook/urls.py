from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/customer/', views.register_customer, name='register_customer'),
    path('register/seller/', views.register_seller, name='register_seller'),
    path('register/admin/', views.register_admin, name='register_admin'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('approve_seller/<int:seller_id>/', views.approve_seller, name='approve_seller'),
    path('unapprove_seller/<int:seller_id>/', views.unapprove_seller, name='notapprove_seller'),
    path('product/',views.product,name='products')
]