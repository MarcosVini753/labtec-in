from rest_framework import mixins, viewsets
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render

from apps.common.viewsets import PublicReadOnlyModelViewSet
from apps.partnerships.models import ContactMessage, Partner
from apps.partnerships.serializers import ContactMessageSerializer, PartnerSerializer


class PartnerViewSet(PublicReadOnlyModelViewSet):
    queryset = Partner.objects.prefetch_related("units")
    serializer_class = PartnerSerializer
    search_fields = ("name", "description")


class ContactMessageViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = ContactMessage.objects.none()
    serializer_class = ContactMessageSerializer
    http_method_names = ["post", "options"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            if request.headers.get("HX-Request"):
                return render(
                    request,
                    "portal/partials/contact_feedback.html",
                    {"errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        if request.headers.get("HX-Request"):
            return render(
                request,
                "portal/partials/contact_feedback.html",
                {"success": True},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
