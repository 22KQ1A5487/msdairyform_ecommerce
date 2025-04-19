from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('cart/', views.cart_view, name='cart'),
    path('products/', views.products_view, name='products'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('order/<int:order_id>/', views.order_detail_view, name='order_detail'),
    path('order_history/', views.order_history_view, name='order_history'),
    path('order_success/', views.order_success, name='order_success'),
    path('contact/', views.contact_view, name='contact'),     
    path('place_order/', views.place_order, name='place_order'),
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('payment/', views.payment, name='payment'),
    path('process-payment/', views.process_payment, name='process_payment'),
    # urls.py
    path('admin/manage-orders/', views.manage_orders, name='manage_orders'),
    path('admin/update-order/<int:order_id>/', views.update_order_status, name='update_order_status'),

    path('profile/', views.profile_view, name='profile'),     
]



