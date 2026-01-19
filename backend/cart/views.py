from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Cart, CartItem
from products.models import Product


# Create your views here.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    user = request.user
    product_id = request.data.get("product_id")
    quantity = int(request.data.get("quantity",1))

    product = Product.objects.get(id=product_id)

    if product.stock < quantity:
        return Response({"error": "Insufficient stock"}, status=400)

    cart = Cart.objects.get(user=user)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, 
        product=product
    )

    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity

    cart_item.save()

    return Response({"message": "Product added to cart"})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_cart(request):
    cart = Cart.objects.get(user=request.user)

    items = []
    subtotal = 0

    for item in cart.items.all():
        total_price = item.product.price * item.quantity
        subtotal += total_price

        items.append({
            "id": item.id,
            "product_id": item.product.id,
            "name": item.product.name,
            "price": item.product.price,
            "quantity": item.quantity,
            "total": total_price
        })

    return Response({
        "items": items,
        "subtotal": subtotal
    })
