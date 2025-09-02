import os
import json
from dotenv import load_dotenv
from typing import TypedDict, List

# --- Importações do LangChain e LangGraph ---
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END

# --- 1. CONFIGURAÇÃO INICIAL E CARREGAMENTO DE DADOS ---

# Carrega as variáveis de ambiente (sua chave Gemini API) do arquivo .env
load_dotenv()

# --- CORREÇÃO APLICADA AQUI ---
# Lemos a chave da API e a guardamos em uma variável.
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Verificamos se a chave foi carregada corretamente.
if not gemini_api_key:
    raise ValueError("A chave GEMINI_API_KEY não foi encontrada no arquivo .env")

# Carrega nossa base de conhecimento "dummy"
with open('noticias_db.json', 'r', encoding='utf-8') as f:
    noticias = json.load(f)

# Extrai apenas o texto das notícias para indexação
textos_noticias = [item['texto'] for item in noticias]

# --- 2. CRIAÇÃO DA BASE DE CONHECIMENTO VETORIAL (FAISS) ---

print("Criando o índice vetorial com FAISS...")
# --- CORREÇÃO APLICADA AQUI ---
# Passamos a chave de API diretamente para o serviço de embeddings.
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=gemini_api_key)

# Cria o índice FAISS em memória a partir dos textos das notícias
vectorstore = FAISS.from_texts(texts=textos_noticias, embedding=embeddings)

# Cria um "retriever", que é a ferramenta para buscar informações no índice FAISS
retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

print("Índice FAISS criado com sucesso.")

# --- 3. DEFINIÇÃO DO MODELO E PROMPTS ---

# --- CORREÇÃO APLICADA AQUI ---
# Passamos a chave de API diretamente para o modelo de chat.
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3, google_api_key=gemini_api_key)

# Template do prompt que usaremos para o agente.
prompt_template = """Você é um assistente especializado em responder perguntas sobre notícias de educação no Distrito Federal.
Use SOMENTE o contexto fornecido abaixo para formular sua resposta.
Se a resposta não estiver no contexto, diga "Com base nas notícias que tenho acesso, não encontrei informações sobre isso."
Seja direto e conciso.

CONTEXTO:
{contexto}

PERGUNTA:
{pergunta}

RESPOSTA:
"""
prompt = ChatPromptTemplate.from_template(prompt_template)

# --- 4. CONSTRUÇÃO DO GRAFO COM LANGGRAPH (Nenhuma alteração aqui) ---

class AgentState(TypedDict):
    pergunta: str
    contexto: List[str]
    resposta: str

def retrieve_context(state: AgentState):
    print("---(NÓ: Buscando Contexto)---")
    pergunta = state["pergunta"]
    docs = retriever.invoke(pergunta)
    contexto_formatado = [doc.page_content for doc in docs]
    return {"contexto": contexto_formatado}

def generate_response(state: AgentState):
    print("---(NÓ: Gerando Resposta)---")
    pergunta = state["pergunta"]
    contexto = state["contexto"]
    rag_chain = prompt | llm | StrOutputParser()
    resposta = rag_chain.invoke({"pergunta": pergunta, "contexto": contexto})
    return {"resposta": resposta}

print("Construindo o grafo com LangGraph...")
workflow = StateGraph(AgentState)
workflow.add_node("recuperador", retrieve_context)
workflow.add_node("gerador", generate_response)
workflow.set_entry_point("recuperador")
workflow.add_edge("recuperador", "gerador")
workflow.add_edge("gerador", END)
app = workflow.compile()
print("Grafo construído e compilado.")

# --- 5. EXECUÇÃO E INTERAÇÃO COM O USUÁRIO (Nenhuma alteração aqui) ---

print("\n--- Agente Conversacional Pronto ---")
print("Digite 'sair' para terminar.")

while True:
    user_input = input("\nVocê: ")
    if user_input.lower() == 'sair':
        break
    inputs = {"pergunta": user_input}
    final_state = app.invoke(inputs)
    print(f"Agente: {final_state['resposta']}")