from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib import messages
from .forms import UserRegistrationForm
from urllib.parse import unquote


# Models Importation
from .models import (
    Topping,
    Menu_Item,
    Profile,
    Extras,
    Order,
    OrderItem,
    User,
    News,
)

import datetime


def index(request):
    if not request.user.is_authenticated:
        return render(request, "login.html", {"message": None})

    Menu = Menu_Item.objects.exclude(category__icontains="Topping").exclude(
        category__icontains="Extra"
    )

    Orders = Order.objects.filter(owner=request.user.profile, is_ordered=False)
    Cart = []

    item_count = 0

    if Orders.exists():
        user_order = Orders[0]
        user_order_items = user_order.ordered_items.all()
        Cart = [menu_item.menu_item for menu_item in user_order_items]

        # toma el numero de items en el carrito
        item_count = user_order.ordered_items.count()

    context = {
        "current_order_products": Cart,
        "item_count": item_count,
        "user": request.user,
        "menu_item": Menu.order_by("-category"),
    }
    return render(request, "index.html", context)


# USER LOGIN VIEW
def login_view(request):
    if request.method == "GET":
        return render(request, "login.html")

    username = request.POST["username"]
    password = request.POST["password"]
    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)
        return redirect("/")
    else:
        return render(request, "login.html", {"message": "Datos invalidos."})


# USER LOGOUT
def logout_view(request):
    logout(request)
    return render(request, "login.html", {"message": "Has Cerrado Sesion"})


# USER REGISTRATION (Im Using the Default Django User Model)
def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/")
    else:
        form = UserRegistrationForm()

    return render(request, "register.html", {"form": form})


# CART ITEM ADDITION
@login_required()
def add_to_cart(request, **kwargs):
    user_profile = get_object_or_404(Profile, user=request.user)

    menu_item = Menu_Item.objects.filter(
        id=kwargs.get("item_id", "")
    ).first()  # ID Obtenido del Form

    quantity = int(request.POST["quantity"])

    for x in range(quantity):
        order_item = OrderItem.objects.create(menu_item=menu_item)

        user_order, status = Order.objects.get_or_create(
            owner=user_profile, is_ordered=False
        )

        user_order.ordered_items.add(order_item)

    if status:
        user_order.save()
        print("Item Saved")

    messages.info(request, f" {quantity} {menu_item.sizes} {menu_item.name} Added")

    return redirect("/")


# CART CONTENT CHECK


@login_required()
def get_user_pending_order(request):
    user_profile = get_object_or_404(Profile, user=request.user)
    order = Order.objects.filter(owner=user_profile, is_ordered=False)
    if order.exists():
        return order[0]
    return 0


@login_required()
def order_details(request, **kwargs):
    existing_order = get_user_pending_order(request)
    user_profile = get_object_or_404(Profile, user=request.user)
    order = Order.objects.filter(owner=user_profile, is_ordered=False)

    context = {
        "order": existing_order,
    }
    return render(request, "cart.html", context)


# ORDER CUSTOMIZATION
@login_required()
def customize_order(request, food, *args, **kwargs):
    if request.method == "GET":
        toppings = Menu_Item.objects.filter(category__contains="Topping")

        extras = Extras.objects.all()

        extra_cheese = Extras.objects.filter(name__icontains="cheese")

        menu_items = Menu_Item.objects.all()

        ordered_item = Menu_Item.objects.filter(name=food).first()

        context = {
            "ordered_item": ordered_item,
            "user": request.user,
            "menu_item": menu_items,
            "toppings": toppings,
            "extras": extras,
            "extra_cheese": extra_cheese,
        }
        return render(request, "custom.html", context)

    user_profile = get_object_or_404(Profile, user=request.user)

    menu_item = Menu_Item.objects.filter(name=food).first()
    print(f"this is menu item in get {menu_item}")

    toppings = []

    if "Special" in food:
        special_toppings = request.POST.getlist("special_toppings")
        print(f"special_toppings:{special_toppings} \n")
        toppings = special_toppings

        if len(toppings) < 4:
            messages.info(
                request,
                "Elegiste menos de 4 ingredientes! \
             una pizza especial necesita \
            4 o mas ingredientes! ",
            )

            menu_items = Menu_Item.objects.all()
            toppings = Menu_Item.objects.filter(category__contains="Topping")
            menu_items = Menu_Item.objects.all()
            ordered_item = Menu_Item.objects.filter(name=food).first()

            context = {
                "ordered_item": ordered_item,
                "user": request.user,
                "menu_item": menu_items,
                "toppings": toppings,
            }
            return render(request, "custom.html", context)

    if "Special" not in food and "Pizza" in food:
        topping1 = request.POST["topping1"]
        toppings.append(topping1)

        try:
            topping2 = request.POST["topping2"]
            toppings.append(topping2)
        except MultiValueDictKeyError:
            toppings2 = False

        try:
            topping3 = request.POST["topping3"]
            toppings.append(topping3)

        except MultiValueDictKeyError:
            topping3 = False

    # get the extras
    extras = []

    num_extras = 0

    if menu_item.category == "Subs":
        sub_extras = request.POST.getlist("sub_extras")

        for extra in sub_extras:
            extras.append(extra + "+ .50c")
            num_extras += 1

    sub_extra = Menu_Item.objects.get(name="Sub_Extra")

    extra_price = sub_extra.price
    extras_cost = num_extras * extra_price

    quantity = int(request.POST["quantity"])

    for x in range(quantity):
        order_item = OrderItem.objects.create(
            menu_item=menu_item,
            ptoppings=toppings,
            extras=extras,
            num_extras=num_extras,
            extras_cost=extras_cost,
        )

        user_order, status = Order.objects.get_or_create(
            owner=user_profile, is_ordered=False
        )

        user_order.ordered_items.add(order_item)

    if status:
        user_order.save()

    messages.info(
        request,
        f" {quantity} {menu_item.sizes} {menu_item.name} \
                            añadido al carrito",
    )

    return redirect('/')


def allorders(request):

    profiles = Profile.objects.all()
    all_orders = Order.objects.filter(is_ordered=True)

    context = { 'all_orders': all_orders}

    return render(request, "orders.html", context)

# Summary View
@login_required()
def order_details(request, **kwargs):

    existing_order = get_user_pending_order(request)
    user_profile = get_object_or_404(Profile, user=request.user)
    order = Order.objects.filter(owner=user_profile, is_ordered=False)

    context = {
        'order': existing_order,
    }
    return render(request, 'summary.html', context)


#Check View
@login_required()
def check(request, **kwargs):
    existing_order = get_user_pending_order(request)

    context = {
        'order': existing_order,
    }

    return render(request, 'check.html', context)