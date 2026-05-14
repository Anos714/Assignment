from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from chats.views import ChatSessionViewSet
from documents.views import DocumentViewSet

router = DefaultRouter()
router.register("documents", DocumentViewSet, basename="documents")
router.register("chats", ChatSessionViewSet, basename="chats")

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/dashboard/", include("dashboard.urls")),
    path("api/", include(router.urls)),
]
