from django.contrib import admin

from documents.models import Document, DocumentChunk


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("filename", "user", "file_type", "status", "chunk_count", "created_at")
    list_filter = ("status", "file_type", "created_at")
    search_fields = ("filename", "user__email")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ("document", "chunk_index", "page_number", "created_at")
    search_fields = ("document__filename", "content")
    readonly_fields = ("id", "created_at")

