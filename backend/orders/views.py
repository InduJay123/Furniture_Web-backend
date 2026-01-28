from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Order, OrderItem
from .serializers import OrderSerializer
from cart.models import Cart
from decimal import Decimal

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def place_order(request):
    user = request.user

    try:
        cart = Cart.objects.get(user=user)
    except:
        return Response({"details":"Cart not found"}, status=status.HTTP_404_NOT_FOUND)

    cart_items = cart.items.select_related("product").all()
    if not cart_items.exists():
        return Response({"details":"Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

    payload = request.data or {}
    email = payload.get("email")
    phone = payload.get("phone")
    first_name = payload.get("first_name")
    last_name = payload.get("last_name")
    address = payload.get("address")
    city = payload.get("city")
    state = payload.get("state")
    zip_code = payload.get("zip_code")

    subtotal = Decimal("0.00")
    order_items_data = []
    
    for ci in cart_items:
        p = ci.product
        price = Decimal(str(p.price))
        qty = int(ci.quantity)
        line_total = price * qty
        subtotal += line_total

        order_items_data.append({
            "product_id": p.id,
            "name": getattr(p, "name", ""),
            "price": price,
            "quantity": qty,
            "category": getattr(p, "category", "") if hasattr(p, "category") else "",
            "image": getattr(p, "image_url", None) if hasattr(p, "image_url") else None,
        }) 

    shipping = Decimal("0.00")  
    total = subtotal + shipping

    # 4) Create order
    order = Order.objects.create(
        user=user,
        email=email,
        phone=phone,
        first_name=first_name,
        last_name=last_name,
        address=address,
        city=city,
        state=state,
        zip_code=zip_code,
        subtotal=subtotal,
        shipping=shipping,
        total=total,
        status="PENDING",
    )

    # 5) Create order items
    OrderItem.objects.bulk_create([
        OrderItem(order=order, **item) for item in order_items_data
    ])

    # 6) Clear cart
    cart_items.delete()

    return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_orders(request):
    order = (
        Order.objects.filter(user=request.user)
        .prefetch_related("items")
        .order_by("-created_at")
    )
    return Response(OrderSerializer(order, many=True).data, status=status.HTTP_200_OK)