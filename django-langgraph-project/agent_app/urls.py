# agent_app/urls.py

from django.urls import path
from .views import run_agent_view

urlpatterns = [
    path('invoke/', run_agent_view, name='invoke_agent'),
]