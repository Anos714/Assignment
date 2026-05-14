from django.contrib import admin

from chats.models import ChatMessage, ChatSession, MessageCitation


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "created_at", "updated_at")
    search_fields = ("title", "user__email")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("chat_session", "role", "answer_status", "created_at")
    list_filter = ("role", "answer_status", "created_at")
    search_fields = ("content", "chat_session__title", "chat_session__user__email")
    readonly_fields = ("id", "created_at")


@admin.register(MessageCitation)
class MessageCitationAdmin(admin.ModelAdmin):
    list_display = ("document_name", "score", "message", "created_at")
    search_fields = ("document_name", "quoted_text")
    readonly_fields = ("id", "created_at")

