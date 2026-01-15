from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Product
from .serializers import ProductSerializer
from .utils import upload_image

from rest_framework.generics import ListAPIView

class ProductCreateView(APIView):
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
            'price': request.data['price'],
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