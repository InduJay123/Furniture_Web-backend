from django.urls import path
from .views import ProductCreateView, ProductListView

urlpatterns = [
    path('add/', ProductCreateView.as_view()),
    path('list/', ProductListView.as_view()),
]