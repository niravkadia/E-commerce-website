import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_project.settings')
django.setup()

from store.models import Category, Product, Order, OrderItem
from django.contrib.auth.models import User

# Clear existing data (optional, but good for clean check)
OrderItem.objects.all().delete()
Order.objects.all().delete()
Product.objects.all().delete()
Category.objects.all().delete()

# Create Categories
cat1 = Category.objects.create(name='Electronics', slug='electronics')
cat2 = Category.objects.create(name='Books', slug='books')

# Create Products
p1 = Product.objects.create(
    category=cat1,
    name='Smartphone',
    slug='smartphone',
    price=599.99,
    description='A powerful smartphone.'
)
p2 = Product.objects.create(
    category=cat2,
    name='Django Book',
    slug='django-book',
    price=29.99,
    description='Learn Django efficiently.'
)

# Create an Order for user 'Nirav'
user = User.objects.get(username='Nirav')
order = Order.objects.create(
    user=user,
    total_price=629.98,
    status='Completed',
    stripe_payment_intent_id='pi_12345'
)

# Add items to Order
OrderItem.objects.create(order=order, product=p1, price=599.99, quantity=1)
OrderItem.objects.create(order=order, product=p2, price=29.99, quantity=1)

print("Dummy data added successfully!")
