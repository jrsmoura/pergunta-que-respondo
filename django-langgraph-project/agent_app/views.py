# agent_app/views.py

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from langchain_core.messages import HumanMessage

# Importa o grafo compilado do nosso outro arquivo
from .graph_builder import compiled_graph

@csrf_exempt # Use apenas para teste, em produção use autenticação adequada
def run_agent_view(request):
  # TODO Implementar
  return None