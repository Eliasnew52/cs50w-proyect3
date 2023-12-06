from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib import messages


#Models Importation
from .models import (Topping, Menu_Item, Profile,
Extras, Order, OrderItem,  User, News, )

import datetime


@login_required()
def index(request):

    if not request.user.is_authenticated:
        return render(request, "login.html", {"message": None})

    Menu = Menu_Item.objects.exclude(category__icontains="Topping").exclude(category__icontains="Extra")

    Orders = Order.objects.filter(owner=request.user.profile, is_ordered=False)
    Cart = []

    item_count = 0

    if Orders.exists():
        user_order = Orders[0]
        user_order_items = user_order.ordered_items.all()
        current_order_products = [menu_item.menu_item for menu_item in user_order_items]

        #toma el numero de items en el carrito
        item_count = user_order.ordered_items.count()

    context ={

        'cart': Cart,
        'item_count': item_count,
        "user": request.user,
        "menu_item": Menu.order_by('-category')
    }
    return render(request, "index.html", context)


# USER LOGIN VIEW
def login_view(request):

    if request.method == "GET":

        return render(request,"login.html")

    username = request.POST["username"]
    password = request.POST["password"]
    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "login.html", {"message": "Datos invalidos."})
