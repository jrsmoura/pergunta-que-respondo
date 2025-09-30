# core/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('agent/', include('agent_app.urls')), # Inclui as URLs da nossa app
]