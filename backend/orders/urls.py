from django.urls import path
from .views import place_order,list_orders,admin_list_orders, admin_update_order_status,admin_order_pdf

urlpatterns = [
    path("place/", place_order),
    path("list/", list_orders),
    path("admin/list/", admin_list_orders),
    path("admin/<int:pk>/status/", admin_update_order_status),
    path("admin/<int:order_id>/pdf/", admin_order_pdf), 
]