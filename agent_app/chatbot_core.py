import os
from typing import TypedDict, List

# langchain
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END

from knowledge.knowledge import create_dummies

class GraphState(TypeDict):
    question: str
    documents: List[str]
    generetion: str

embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001",
    google_api_key = os.getenv("GOOGLE_API_KEY")
)

texts = create_dummies()

vector_store = FAISS.from_text(
    texts=texts
    embedding =embeddings    
)

retriever = vector_store.as_retriever()

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

prompt_template = """Você é um assistente para responder perguntas sobre notícias de educação no Distrito Federal.
Use apenas o contexto fornecido para responder. Se a pergunta não estiver no contexto, diga "Apenas respondo sobre informações de notícias de educação no Distrito Federal."
Seja direto e conciso.

CONTEXTO:
{contexto}

PERGUNTA:
{pergunta}

RESPOSTA:
"""
prompt = ChatPromptTemplate.from_template(prompt_template)

def retrieve_context(state: AgentState):
    pergunta = state["pergunta"]
    docs = retriever.invoke(pergunta)
    format_context = [doc.page_content for doc in docs]
    return {"contexto": format_context}

def generate_response(state: AgentState):
    pergunta = state["pergunta"]
    contexto = state["contexto"]
    rag_chain = prompt | llm | StrOutputParser()
    resposta = rag_chain.invoke({"pergunta": pergunta, "contexto": contexto})
    return {"resposta": resposta}

def build_graph():
    workflow = StateGraph(GraphState)

    workflow.add_node("retriever", retrieve_context)
    workflow.add_node("response", generate_response)
    workflow.set_entry_point("retriever")
    workflow.add_edge("retriever", "response")
    workflow.add_edge("response", END)
    app = workflow.compile()
    
    return app