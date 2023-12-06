from __future__ import unicode_literals
from django.conf import settings
from django.db import models

from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save


User = get_user_model()

# Create your models here.


class Menu_Item(models.Model):

    MENU_CATEGORIES = (
    ('Pizza', 'Pizza'),
    ('Pasta', 'Pasta'),
    ('Subs', 'Subs'),
    ('Salad', 'Salad'),
    ('Dinner_Platter', 'Dinner_Platter'),
    ('Topping', 'Topping'),
    ('Extra', 'Extra'),
    ('Dessert', 'Dessert'),
    ('Pastry', 'Pastry'),
    ('Main', 'Main'),
    ('Appetizer', 'Appetizer'),
    ('Side', 'Side'),
    ('Miscellaneous', 'Miscellaneous')
    )

    SIZE_CATEGORIES = (
    ('Sm', 'Small'),
    ('Md', 'Medium'),
    ('Lg', 'Large'),
    ('XL', 'Extra_Large')
    )


    category = models.CharField(max_length=36, null=True, blank=True,
                                choices=MENU_CATEGORIES,
                                help_text='Categoría del elemento del menú.')

    name = models.CharField(max_length=128,
                            help_text='Nombre del elemento del menú')

    price =  models.DecimalField(max_digits=4, null=True, blank=True,
                                decimal_places=2, default=0.00)

    sizes = models.CharField(max_length=4, null=True, blank=True,
                                choices=SIZE_CATEGORIES,
                                help_text='Ingrese el tamaños \
                                            del elemento del menú')

    toppings = models.CharField( max_length=400, blank=True, null=True,
                                help_text='Introducir ingredientes')

    num_toppings = models.CharField(max_length=10, blank=True, null=True)


    def __str__(self):
        return f" Category:{self.category} - Name:{self.name} - \
        Sizes:{self.sizes} - Price: {self.price} \
        -numtoppings {self.num_toppings} - toppings {self.toppings}"





class Topping(models.Model):

    topping_name = models.CharField(max_length=36)

    price = models.DecimalField(max_digits=4, null=True, blank=True,
                                decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.topping_name}"

class Extras(models.Model):
    name = models.CharField(max_length=64, help_text='Introduce el nombre del extra')

    price = models.DecimalField(max_digits=4,decimal_places=2,
                        default=0, help_text='Introduzca el precio del extra')

    def __str__(self):
        return f"{self.name} - {self.price}"



class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)

    menu_items = models.ManyToManyField(Menu_Item, blank=True)


    def __str__(self):
        return f"{self.user.username}"


def post_save_profile_create(sender, instance, created, *args, **kwargs):
    if created:
        user_profile, created = Profile.objects.get_or_create(user=instance)

post_save.connect(post_save_profile_create, sender=settings.AUTH_USER_MODEL)

class OrderItem(models.Model):
    menu_item = models.ForeignKey(Menu_Item,on_delete=models.CASCADE,
                                    blank=True, null=True)

    is_ordered = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now=True)
    date_ordered = models.DateTimeField(null=True)
    is_topping =models.BooleanField(default=False)
    num_extras = models.IntegerField( blank=True, default=0)
    extras = models.CharField(max_length=400,  blank=True, null=True)
    extras_cost = models.DecimalField(max_digits=4,decimal_places=2, default = 0.00)
    ptoppings = models.CharField(max_length=400,  blank=True, null=True)
    def __str__(self):
            return f"Menu-Item: {self.menu_item} - \
                Toppings: {self.ptoppings}\
                - Num extras:{self.num_extras} \
                - sub_extras {self.extras} \
                status:{self.is_ordered} \
                Date ordered: {self.date_added} - \
            "


class Order(models.Model):
    ref_code = models.CharField(max_length=15, blank=True)
    owner = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True)
    is_ordered = models.BooleanField(default=False)
    ordered_items = models.ManyToManyField(OrderItem)
    date_ordered = models.DateTimeField(auto_now=True)

    # retorna las ordenes
    def num_order_items(self):
        return self.order_items.count()

    #obtener todos los pedidos
    def get_cart_ordered_items(self):
        return self.ordered_items.all()
        #exclude(is_topping=True)

    def get_cart_ordered_items_toppings(self):
        return self.ordered_items.all()
        #sum of total price of all ordered_items

    def get_cart_total(self):

    #    Extra = Menu_Item.objects.filter(name="Sub_Extra")

        return sum([item.menu_item.price for item in self.ordered_items.all()]
        + [item.extras_cost for item in self.ordered_items.all()])


    def __str__(self):
        return f" User: {self.owner} ---- \
        Date ordered; {self.date_ordered}----\n \
        Order Complete Status: {self.is_ordered}---- \n \
        Total Price: {self.get_cart_total()} ---- \n \
        Ordered Items:{self.ordered_items.all()} -- \
        "


class News(models.Model):
    title = models.CharField(max_length=50)
    content = models.TextField(max_length=1000)
    description = models.TextField(max_length=100)
    fecha = models.DateTimeField()

    def __str__(self):
        return f" title:{self.title} - content:{self.content} - \
        Description:{self.description} - fecha:{self.fecha}"
