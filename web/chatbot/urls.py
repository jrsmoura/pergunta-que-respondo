"""
Configuração de URLs para o aplicativo chatbot.

Este módulo define os padrões de URL para o app chatbot, mapeando URLs para suas respectivas funções de visualização.

Rotas:
    - "": Rota raiz que renderiza a homepage com um modal fixo.
    - "chat/": Rota para a interface web do chatbot.
    - "ask/": Rota para a API JSON que lida com perguntas ao chatbot
    - "update_news/": Rota para executar o crawler e atualizar notícias.
Cada rota está associada a uma função de visualização que processa as requisições e retorna respostas apropriadas.

Importações:
    - path: Função do Django para definir padrões de URL.
    - views: Módulo que contém as funções de visualização do app chatbot.
    - homepage: View que renderiza a página inicial com um modal fixo.
    - ask: View que lida com consultas ao chatbot via API.
    - chat_interface: View que renderiza a interface web do chatbot.
    - update_news: View que executa o crawler para atualizar notícias.
"""

from django.urls import path
from . import views
from .views import ask, chat_interface, update_news, homepage

urlpatterns = [
    path("", homepage, name="homepage"),          # homepage com modal fixo
    path("chat/", chat_interface, name="chat"),   # interface web do chatbot
    path("ask/", ask, name="ask"),                # API JSON
    path("update_news/", update_news, name="update_news"),  # endpoint crawler
]