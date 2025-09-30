# agent_app/graph_builder.py

import os
from typing import TypedDict, Annotated, Sequence
import operator
from dotenv import load_dotenv

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.graph import StateGraph, END

# Carrega as variáveis de ambiente (API Keys) do arquivo .env
load_dotenv()

# 1. Definição da Ferramenta
#    Para este exemplo, usaremos o Tavily Search para buscar na web.
tool = TavilySearchResults(max_results=2)
tools = [tool]

# 2. Definição do Estado do Agente (AgentState)
#    É a "memória" do nosso agente, que passa de um nó para outro no grafo.
class AgentState(TypedDict):
  # TODO Implementar
  
  # 3. Definição dos Nós do Grafo
  #    Nós são as funções que realizam o trabalho.

  # Nó que chama o modelo (LLM)
  def call_model(state):
    # TODO Implementar
    return None 
  # Nó que chama uma ferramenta
  def call_tool(state):
    # TODO Implementar
    return None
  # 4. Definição das Bordas Condicionais (Conditional Edges)
  #    Decide qual nó executar a seguir.
  def should_continue(state):
    # TODO Implementar
    return None
  # 5. Construção e Compilação do Grafo
def build_graph():
  # TODO Implementar
  return None
# Instancia o grafo compilado para ser importado pelo Django
compiled_graph = build_graph()