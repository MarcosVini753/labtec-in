from rest_framework import serializers

from apps.axes.serializers import ResearchAxisSerializer
from apps.institutional.serializers import InstitutionalUnitSummarySerializer
from apps.news.models import Post, PostLink


class PostLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostLink
        fields = ("label", "url", "display_order")


class PostSerializer(serializers.ModelSerializer):
    unit = InstitutionalUnitSummarySerializer(read_only=True)
    axis = ResearchAxisSerializer(read_only=True)
    links = PostLinkSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "unit",
            "title",
            "slug",
            "axis",
            "summary",
            "content",
            "cover_image",
            "body_image",
            "published_at",
            "links",
        )
