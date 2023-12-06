from django.contrib import admin

# Register your models here.
from .models import (Menu_Item,  Extras, Order, OrderItem, Profile, News, )

admin.site.register(Menu_Item)
admin.site.register(Extras)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Profile)
admin.site.register(News)