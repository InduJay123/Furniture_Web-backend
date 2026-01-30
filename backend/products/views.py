from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Product
from .serializers import ProductSerializer
from .utils import upload_image
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser
from rest_framework.generics import ListAPIView, RetrieveAPIView

class ProductCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    def post(self, request):
        image = request.FILES.get('image')

        if not image:
            return Response(
                {"error": "Image file is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        image_url = upload_image(image)

        data = {
            'name': request.data['name'],
            'category': request.data['category'],
            'sku': request.data.get('sku', ''),
            'description': request.data.get('description', ''),
            'price': request.data['price'],
            'stock_qty': request.data.get('stock_qty', 0),
            'out_of_stock': request.data.get('out_of_stock', False),    
            'weight': request.data.get('weight', None),
            'dimensions': request.data.get('dimensions', ''),
            'image_url': image_url
        }

        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductListView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny] 

class ProductDetailView(RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

class ProductUpdateDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        image = request.FILES.get('image')
        if image:
            image_url = upload_image(image)
            request.data['image_url'] = image_url

        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)