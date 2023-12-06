from django.urls import path

from . import views



urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    #path("register", views.register_view, name="register"),

    #Cart Manipulation
    path('add-to-cart/<int:item_id>', views.add_to_cart, name="add_to_cart"),
    path('ordersummary/', views.order_details, name="ordersummary"),
]
