from rest_framework import serializers


class SearchResultSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    product_name = serializers.CharField()
    description = serializers.CharField()
    category = serializers.CharField()
    tags = serializers.ListField(child=serializers.CharField())
    relevance_score = serializers.FloatField()
    rank_reason = serializers.CharField()
