# admin_panel/views_api.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.store.models import Product
from .serializers import ProductStockSerializer

class ProductStockAPIView(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductStockSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)