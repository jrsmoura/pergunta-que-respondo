"""
Configuração de URLs para o aplicativo chatbot.

Este módulo define os padrões de URL para o app chatbot, mapeando URLs para suas respectivas funções de visualização.

Rotas:
    - "ask/": Mapeia para a view 'ask', que lida com requisições de API para interações com o chatbot (retorna JSON).
    - "interface/": Mapeia para a view 'chat_interface', que serve a interface web do chatbot.

Importações:
    - path: Função do Django para definir padrões de URL.
    - ask: View que lida com consultas ao chatbot via API.
    - chat_interface: View que renderiza a interface web do chatbot.
"""
from django.urls import path

from .views import ask, chat_interface

urlpatterns = [
    path("ask/", ask, name="ask"),     # API JSON em /ask/
    path("", chat_interface, name="chat"),  # interface web direto na raiz
]