from rest_framework import generics, status
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import RegisterSerializer
from rest_framework.permissions import AllowAny

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status

class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

class EmailLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "No active account found with the given credentials"}, status=401)

        user = authenticate(username=user_obj.username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            })

        return Response({"detail": "No active account found with the given credentials"}, status=401)

class AdminLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "Invalid credentials"}, status=401)

        user = authenticate(username=user_obj.username, password=password)
        if not user:
            return Response({"detail": "Invalid credentials"}, status=401)

        #Admin check
        if not user.is_staff:
            return Response({"detail": "Not an admin account"}, status=403)

        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "is_admin": True,        
            "username": user.username,
            "email": user.email,
        })

from django.contrib.auth.models import User
from django.db.models import Count, Sum, Max
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from orders.models import Order
from .serializers import CustomerAdminSerializer

class AdminCustomerListView(ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = CustomerAdminSerializer

    def get_queryset(self):
        qs = User.objects.filter(is_staff=False)

        # join orders by related_name="orders" (Order model: user = ForeignKey(..., related_name="orders"))
        qs = qs.annotate(
            orders_count=Count("orders", distinct=True),
            total_spent=Sum("orders__total"),
            last_order=Max("orders__created_at"),
        ).order_by("-last_order")

        return qs