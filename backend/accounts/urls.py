from django.urls import path
from .views import RegisterView, EmailLoginView, AdminLoginView,AdminCustomerListView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", EmailLoginView.as_view(), name="login"),

    path("admin/login/", AdminLoginView.as_view(), name="admin-login"),
    path("admin/customers/", AdminCustomerListView.as_view(), name="admin-customers"),
]