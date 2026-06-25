from rest_framework import generics, permissions

from catalog.serializers import ProductSerializer
from catalog.services import list_products


class ProductListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProductSerializer
    queryset = list_products()


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProductSerializer
    queryset = list_products()
