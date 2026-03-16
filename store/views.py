from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product

def home(request):
    # Public Landing Page - Static-ish professional marketing
    return render(request, 'store/home.html')

def check_authentication(request):
    return render(request, 'store/check_auth.html')

@login_required(login_url='check_auth')
def product_list(request):
    # Only authenticated users see products
    products = Product.objects.filter(available=True)
    return render(request, 'store/products.html', {'products': products})

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, 'Account created successfully!')
        return redirect('home')
        
    return render(request, 'store/register.html')

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, 'Logged in successfully')
            return redirect('product_list')
        else:
            messages.error(request, 'Invalid credential')
    return render(request, 'store/login.html')

def logout(request):
    auth_logout(request)
    messages.info(request, 'Logged out successfully.')
    return redirect('home')
