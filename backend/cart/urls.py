from django.urls import path
from .views import add_to_cart, view_cart, update_cart_item,remove_cart_item

urlpatterns = [
    path("add/", add_to_cart),
    path("view/", view_cart),
    path("update/", update_cart_item),
    path("remove/", remove_cart_item),
]