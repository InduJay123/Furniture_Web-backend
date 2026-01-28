from django.urls import path
from .views import place_order,list_orders

urlpatterns = [
    path("place/", place_order),
    path("list/", list_orders),
]