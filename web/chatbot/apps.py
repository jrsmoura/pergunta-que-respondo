"""
Configuração do aplicativo Django para o módulo 'chatbot'.
"""

from django.apps import AppConfig

class ChatbotConfig(AppConfig):
    """
    Classe de configuração para o aplicativo Django 'chatbot'.

    Atributos:
        default_auto_field (str): Especifica o tipo de campo de chave primária auto-criada a ser usado para os modelos.
        name (str): O caminho Python completo para o aplicativo.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "chatbot"
