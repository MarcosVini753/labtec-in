from rest_framework import serializers

from apps.axes.serializers import ResearchAxisSerializer
from apps.institutional.serializers import InstitutionalUnitSummarySerializer
from apps.people.serializers import PersonSummarySerializer
from apps.portfolio.models import (
    Project,
    ProjectCategory,
    ProjectLink,
    ProjectResult,
    ProjectStartupProfile,
    ProjectStatus,
    ProjectTeamMember,
)


class ProjectCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectCategory
        fields = ("id", "name", "slug", "description", "display_order")


class ProjectStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectStatus
        fields = ("name", "slug", "display_order")


class ProjectTeamMemberSerializer(serializers.ModelSerializer):
    person = PersonSummarySerializer(read_only=True)

    class Meta:
        model = ProjectTeamMember
        fields = ("person", "role", "is_lead", "display_order")


class ProjectResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectResult
        fields = ("title", "description", "result_type", "file", "external_url", "display_order")


class ProjectLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectLink
        fields = ("label", "url", "link_type", "display_order")


class ProjectStartupProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectStartupProfile
        fields = ("focus_area", "species_or_subject", "institution")


class ProjectSerializer(serializers.ModelSerializer):
    unit = InstitutionalUnitSummarySerializer(read_only=True)
    axis = ResearchAxisSerializer(read_only=True)
    category = ProjectCategorySerializer(read_only=True)
    status = ProjectStatusSerializer(read_only=True)
    team_members = ProjectTeamMemberSerializer(many=True, read_only=True)
    results = ProjectResultSerializer(many=True, read_only=True)
    links = ProjectLinkSerializer(many=True, read_only=True)
    startup_profile = ProjectStartupProfileSerializer(read_only=True, allow_null=True)

    class Meta:
        model = Project
        fields = (
            "id",
            "unit",
            "title",
            "slug",
            "axis",
            "category",
            "area",
            "status",
            "year",
            "summary",
            "problem",
            "solution",
            "cover_image",
            "published_at",
            "team_members",
            "results",
            "links",
            "startup_profile",
        )
