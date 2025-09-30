"""
Módulo de engine RAG para o chatbot.

Responsável por carregar o vetor FAISS e fornecer funções de recuperação de contexto.
"""

import sys
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.cross_encoders.huggingface import HuggingFaceCrossEncoder
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# -------------------------------------------------------------------------
# Configuração base
# -------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

FAISS_DIR = os.path.join(BASE_DIR, "FAISS")
load_dotenv()

# -------------------------------------------------------------------------
# Lazy init – evita quebrar no Sphinx
# -------------------------------------------------------------------------
embeddings = None
vector_store = None
base_retriever = None
retriever = None
llm = None
prompt = None

def init_components():
    """Inicializa embeddings, FAISS, retriever e LLM (usado em runtime)."""
    global embeddings, vector_store, base_retriever, retriever, llm, prompt

    if embeddings is None:
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    if vector_store is None:
        try:
            vs = FAISS.load_local(
                FAISS_DIR,
                embeddings,
                allow_dangerous_deserialization=True
            )
            vector_store = vs
            base_retriever = vs.as_retriever(search_kwargs={"k": 10})
        except Exception:
            vector_store = None
            base_retriever = None

    if retriever is None and base_retriever is not None:
        hf_encoder = HuggingFaceCrossEncoder(
            model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"
        )
        reranker = CrossEncoderReranker(model=hf_encoder, top_n=5)
        retriever = ContextualCompressionRetriever(
            base_compressor=reranker,
            base_retriever=base_retriever,
        )

    if llm is None:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
        )

    if prompt is None:
        template = """Você é um assistente que responde perguntas sobre educação na região da RIDE-DF. Use o contexto fornecido para responder de forma precisa e concisa. Se a pergunta não estiver relacionada ao contexto, responda que não encontrou informações específicas sobre a pergunta. Não invente respostas.

CONTEXTO:
{contexto}

PERGUNTA:
{pergunta}

RESPOSTA:
"""
        prompt = ChatPromptTemplate.from_template(template)


# -------------------------------------------------------------------------
# API pública
# -------------------------------------------------------------------------
def answer_question(pergunta: str) -> dict:
    """
    Responde a uma pergunta utilizando RAG (Retrieval-Augmented Generation).

    Args:
        pergunta (str): Pergunta a ser respondida.

    Returns:
        dict: Um dicionário contendo:
            - "resposta" (str): A resposta gerada.
            - "fontes" (list): Lista de até 3 fontes relevantes.
    """
    # Inicializa só quando necessário
    init_components()

    if retriever is None:
        return {
            "resposta": "Não foi possível inicializar o mecanismo RAG.",
            "fontes": [],
        }

    docs = retriever.invoke(pergunta)
    contexto = [doc.page_content for doc in docs]

    if not contexto or len(" ".join(contexto)) < 50:
        return {
            "resposta": f"Não encontrei notícias específicas sobre '{pergunta}', mas posso trazer informações gerais sobre educação no DF.",
            "fontes": [],
        }

    rag_chain = prompt | llm | StrOutputParser()
    resposta = rag_chain.invoke({"pergunta": pergunta, "contexto": contexto})

    fontes = []
    for doc in docs[:3]:
        meta = getattr(doc, "metadata", {})
        fonte = meta.get("fonte") or meta.get("source") or "Fonte desconhecida"
        snippet = doc.page_content[:200].replace("\n", " ") + "..."
        fontes.append({"fonte": fonte, "snippet": snippet})

    return {"resposta": resposta, "fontes": fontes}


# -------------------------------------------------------------------------
# Evitar que o Sphinx quebre
# -------------------------------------------------------------------------
if os.environ.get("SPHINX_BUILD") != "1":
    init_components()
