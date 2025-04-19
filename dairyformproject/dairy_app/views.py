from django.shortcuts import render, redirect, get_object_or_404
from .models import *
import stripe
from django.http import JsonResponse
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
def home(request):
    return render(request, 'home.html')
def products_view(request):
    products = Product.objects.all()
    return render(request, 'products.html', {'products': products})
def product_detail(request, id):
    product = get_object_or_404(Product, pk=id)
    return render(request, 'product_detail.html', {'product': product})
@staff_member_required
def manage_orders(request):
    orders = Order.objects.all()
    return render(request, 'manage_orders.html', {'orders': orders})
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Use user directly in CartItem
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': 1}
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, f"{product.name} has been added to your cart.")
    return redirect('products')

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect(request.GET.get('next') or 'home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    auth_logout(request)
    return redirect('home')
@login_required
def checkout_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.total_price for item in cart_items)
    
    if request.method == 'POST':
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        
        # Create order
        order = Order.objects.create(user=request.user, address=address, phone=phone, total=total)
        
        # Add cart items to the order
        for item in cart_items:
            order.items.add(item)
        
        # Clear the cart
        cart_items.delete()
        
        return redirect('order_success')  # Redirect to a success page
    
    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'cart_total': total
    })

@login_required
def order_history_view(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'order_history.html', {
        'orders': orders
    })
@login_required
def order_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_detail.html', {'order': order})

def payment(request):
    return render(request, 'payment.html', {'STRIPE_TEST_PUBLIC_KEY': settings.STRIPE_TEST_PUBLIC_KEY})

def process_payment(request):
    if request.method == 'POST':
        token = request.POST.get('stripeToken')
        address = request.POST.get('address')
        phone = request.POST.get('phone')

        try:
            # Process the payment with Stripe
            charge = stripe.Charge.create(
                amount=1000,  # Amount in cents (e.g., 1000 cents = $10)
                currency="usd",
                description="Payment for DairyFarm",
                source=token,
            )

            # You can save the order details (address, phone, etc.) in your database
            # For now, we just return a success response
            return JsonResponse({'success': True, 'charge': charge})

        except stripe.error.StripeError as e:
            return JsonResponse({'success': False, 'error': str(e)})

def products(request):
    return render(request, 'products.html')  # or however you're rendering it
from django.shortcuts import render
def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')or 'no-email@msdairyfarm.com' 
        message = request.POST.get('message')
        ContactMessage.objects.create(name=name, email=email, message=message)
        messages.success(request, "Your message has been received successfully!")
        return redirect('contact')
    
    return render(request, 'contact.html')
    
@login_required
def profile_view(request):
    return render(request, 'profile.html', {'user': request.user})


@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    cart_total = sum(item.total_price for item in cart_items)

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'cart_total': cart_total
    })

@login_required
def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.filter(user=request.user, product=product).first()

    if cart_item:
        cart_item.delete()
        messages.success(request, f"{product.name} removed from your cart.")

    return redirect('cart')

@login_required
def place_order(request):
    if request.method == 'POST':
        address = request.POST.get('address')
        phone = request.POST.get('phone')

        cart_items = CartItem.objects.filter(user=request.user)
        if not cart_items:
            return redirect('cart')

        total = sum(item.total_price for item in cart_items)

        # Create Order (this is the main order)
        order = Order.objects.create(
            user=request.user,
            total=total,
            address=address,
            phone=phone
        )

        # Create OrderItems for each product in the cart
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity
            )

        # Clear the user's cart
        cart_items.delete()

        return redirect('order_success')  # Make sure this view/template exists
    else:
        return redirect('checkout')
@login_required
def order_success(request):
    latest_order = Order.objects.filter(user=request.user).latest('created_at')
    return render(request, 'order_success.html', {'order': latest_order})
@login_required
def mark_order_delivered(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order.status = 'Delivered'
    order.save()
    messages.success(request, "Your order has been marked as delivered.")
    return redirect('order_detail', order_id=order.id)

@staff_member_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f"Order #{order.id} status updated to {new_status}")
    return redirect('manage_orders')
