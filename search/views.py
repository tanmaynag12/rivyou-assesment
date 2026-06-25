from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import SearchResultSerializer
from .services import search_products


class SearchView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        query = request.query_params.get("q", "").strip()
        if not query:
            return Response(
                {"detail": "Search query 'q' is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        results = search_products(query)
        serializer = SearchResultSerializer(results, many=True)

        return Response(
            {
                "query": query,
                "count": len(results),
                "results": serializer.data,
            }
        )
