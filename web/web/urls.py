from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("chatbot.urls")),  # raiz aponta pro app chatbot
]