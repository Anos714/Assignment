from django.core.cache import cache
from rest_framework import mixins, status, viewsets
from rest_framework.response import Response

from documents.models import Document
from documents.serializers import DocumentSerializer, DocumentUploadSerializer
from documents.services import enqueue_document_ingestion


class DocumentViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    def get_queryset(self):
        return Document.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return DocumentUploadSerializer
        return DocumentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        document = serializer.save()
        enqueue_document_ingestion(document)
        cache.clear()
        return Response(DocumentSerializer(document).data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        instance.delete()
        cache.clear()
