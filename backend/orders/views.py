from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated,IsAdminUser
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

    # Create order
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

@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_list_orders(request):
    orders = (
        Order.objects.all()
        .prefetch_related("items")
        .order_by("-created_at")
    )
    return Response(OrderSerializer(orders, many=True).data, status=status.HTTP_200_OK)

@api_view(["PATCH"])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_update_order_status(request, pk):
    try:
        order = Order.objects.get(pk=pk)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

    new_status = request.data.get("status")
    allowed = {"PENDING", "PACKING", "DELIVERED", "CANCELLED"}
    if new_status not in allowed:
        return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

    order.status = new_status
    order.save()
    return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)


import io
import urllib.request
from decimal import Decimal
from django.http import HttpResponse

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

def _safe_draw_image(c, url, x, y, w, h):
    """
    Try to load an image from a public URL and draw it.
    If it fails, just skip.
    """
    if not url:
        return
    try:
        with urllib.request.urlopen(url, timeout=5) as f:
            img_bytes = f.read()
        img = ImageReader(io.BytesIO(img_bytes))
        c.drawImage(img, x, y, w, h, preserveAspectRatio=True, anchor="c", mask="auto")
    except Exception:
        # skip broken image
        pass


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_order_pdf(request, order_id):
    try:
        order = (
            Order.objects
            .select_related("user")
            .prefetch_related("items")
            .get(id=order_id)
        )
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # ---- Header ----
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, height - 50, f"Order Invoice - #{order.id}")

    c.setFont("Helvetica", 10)
    c.drawString(40, height - 70, f"Date: {order.created_at.strftime('%Y-%m-%d %H:%M') if order.created_at else '-'}")
    c.drawString(40, height - 85, f"Status: {order.status}")
    c.drawString(40, height - 100, f"Payment: {getattr(order, 'payment_status', 'PENDING')}")

    # ---- Customer ----
    y = height - 130
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "Customer")
    y -= 16

    c.setFont("Helvetica", 10)
    full_name = f"{order.first_name or ''} {order.last_name or ''}".strip()
    if not full_name:
        full_name = order.user.username if order.user else "Customer"

    c.drawString(40, y, f"Name: {full_name}")
    y -= 14
    c.drawString(40, y, f"Email: {order.email or '-'}")
    y -= 14
    c.drawString(40, y, f"Phone: {order.phone or '-'}")
    y -= 14
    c.drawString(40, y, f"Address: {order.address or '-'}, {order.city or ''} {order.state or ''} {order.zip_code or ''}")
    y -= 22

    # ---- Items header ----
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "Items")
    y -= 14

    # Table columns
    c.setFont("Helvetica-Bold", 10)
    c.drawString(40, y, "Image")
    c.drawString(95, y, "Product")
    c.drawString(320, y, "Qty")
    c.drawString(360, y, "Price")
    c.drawString(440, y, "Line Total")
    y -= 10

    c.line(40, y, width - 40, y)
    y -= 10

    c.setFont("Helvetica", 10)

    for it in order.items.all():
        if y < 120:  # new page
            c.showPage()
            y = height - 60
            c.setFont("Helvetica-Bold", 12)
            c.drawString(40, y, "Items (cont.)")
            y -= 20
            c.setFont("Helvetica", 10)

        # image box
        _safe_draw_image(c, getattr(it, "image", None), 40, y - 38, 45, 45)

        name = getattr(it, "name", "") or "-"
        qty = int(getattr(it, "quantity", 0) or 0)
        price = Decimal(str(getattr(it, "price", 0) or 0))
        line_total = price * qty

        c.drawString(95, y, name[:45])
        c.drawString(320, y, str(qty))
        c.drawString(360, y, f"{price:.2f}")
        c.drawString(440, y, f"{line_total:.2f}")

        y -= 55

    # ---- Totals ----
    y -= 10
    c.line(40, y, width - 40, y)
    y -= 16

    c.setFont("Helvetica-Bold", 11)
    c.drawRightString(width - 40, y, f"Subtotal: {order.subtotal:.2f}")
    y -= 14
    c.drawRightString(width - 40, y, f"Shipping: {order.shipping:.2f}")
    y -= 14
    c.drawRightString(width - 40, y, f"Total: {order.total:.2f}")

    c.showPage()
    c.save()

    pdf = buffer.getvalue()
    buffer.close()

    resp = HttpResponse(pdf, content_type="application/pdf")
    resp["Content-Disposition"] = f'attachment; filename="ORD-{order.id}.pdf"'
    return resp
