from django.contrib import admin

from .models import Product, Order,ContactMessage
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(ContactMessage)