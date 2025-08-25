# agent_app/urls.py

from django.urls import path
from .views import run_agent_view
from . import views

urlpatterns = [
    path('invoke/', run_agent_view, name='invoke_agent'),
    path('', views.chatbot, name='chatbot'),
]