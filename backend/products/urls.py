from django.urls import path
from .views import ProductCreateView, ProductListView, ProductDetailView, ProductUpdateDeleteView

urlpatterns = [
    path('add/', ProductCreateView.as_view()),
    path('list/', ProductListView.as_view()),
    
    path("<int:pk>/", ProductDetailView.as_view()),
    path("<int:pk>/update/", ProductUpdateDeleteView.as_view()),
    path("<int:pk>/delete/", ProductUpdateDeleteView.as_view()),
]