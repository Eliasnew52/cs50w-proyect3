from django.urls import path

from . import views



urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name ="register"),


    #Cart Manipulation
    path('add-to-cart/<int:item_id>', views.add_to_cart, name="add_to_cart"),
    path('ordersummary/', views.order_details, name="ordersummary"),
    path('customize_order/str<food>', views.customize_order, name="customize_order"),


    #Checks
    path('check/', views.check, name='check'),
    path('ordersummary/', views.order_details, name="ordersummary"),

    #All Orders
    path('allorders', views.allorders, name='allorders'),
]

