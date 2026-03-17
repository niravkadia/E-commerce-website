from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Category, Order, OrderItem
from django.conf import settings
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

def home(request):
    # Public Landing Page - Static-ish professional marketing
    return render(request, 'store/home.html')

def check_authentication(request):
    return render(request, 'store/check_auth.html')

@login_required(login_url='check_auth')
def cart_view(request):
    order, created = Order.objects.get_or_create(user=request.user, status='Pending', defaults={'total_price': 0})
    cart_items = order.items.all().order_by('id')
    return render(request, 'store/cart.html', {'cart_items': cart_items, 'cart': order})

@login_required(login_url='check_auth')
def payment_success(request):
    order = Order.objects.get(user=request.user, status='Pending')
    order.status = 'Completed'
    order.save()
    messages.success(request, 'Payment successful! Order completed.')
    return redirect('product_list')

@login_required(login_url='check_auth')
def product_list(request):
    # Only authenticated users see products
    products = Product.objects.filter(available=True)
    return render(request, 'store/products.html', {'products': products})

@login_required(login_url='check_auth')
def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    order, created = Order.objects.get_or_create(user=request.user, status='Pending', defaults={'total_price': 0})
    order_item, created = OrderItem.objects.get_or_create(order=order, product=product, defaults={'price': product.price})
    
    if not created:
        order_item.quantity += 1
        order_item.save()
    else:
        # If it was just created, ensure quantity is 1 (or reset if needed)
        order_item.quantity = 1
        order_item.save()
        
    order.recalculate_total()
    messages.success(request, 'Added to cart!')
    return redirect('product_list')

@login_required(login_url='check_auth')
def update_quantity(request, item_id, action):
    item = OrderItem.objects.get(id=item_id)
    order = item.order

    if action == 'increase':
        item.quantity += 1
    elif action == 'decrease' and item.quantity > 1:
        item.quantity -= 1
    
    item.save()
    order.recalculate_total()
    return redirect('cart_view')

@login_required(login_url='check_auth')
def remove_from_cart(request, item_id):
    item = OrderItem.objects.get(id=item_id)
    order = item.order
    item.delete()
    order.recalculate_total()
    messages.success(request, 'Removed from cart!')
    return redirect('cart_view')

@login_required(login_url='check_auth')
def create_checkout_session(request):
    order = Order.objects.get(user=request.user, status='Pending')
    
    line_items = []
    for item in order.items.all():
        line_items.append({
            'price_data': {
                'currency': 'usd',
                'unit_amount': int(item.price * 100),
                'product_data': {'name': item.product.name},
            },
            'quantity': item.quantity,
        })
        
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=request.build_absolute_uri('/payment-success/'),
        cancel_url=request.build_absolute_uri('/cart/'),
    )
    return redirect(checkout_session.url)

@login_required(login_url='check_auth')
def add_product(request):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to add products.')
        return redirect('home')

    if request.method == 'POST':
        name = request.POST.get('name')
        slug = request.POST.get('slug')
        description = request.POST.get('description')
        price = request.POST.get('price')
        category_id = request.POST.get('category')
        category = Category.objects.get(id=category_id)
        
        product = Product.objects.create(
            name=name,
            slug=slug,
            description=description,
            price=price,
            category=category,
            image=request.FILES.get('image')
        )
        messages.success(request, 'Product added successfully!')
        return redirect('product_list')

    categories = Category.objects.all()
    return render(request, 'store/add_product.html', {'categories': categories})

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
