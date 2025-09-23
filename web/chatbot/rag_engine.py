import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from knowledge import create_dummies

# Embeddings
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# Carregar textos coletados
texts = create_dummies()

# Construir índice FAISS em memória
vector_store = FAISS.from_texts(texts, embedding=embeddings)
retriever = vector_store.as_retriever()

# Modelo LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# Prompt
prompt_template = """Você é um assistente que responde perguntas sobre notícias de educação no Distrito Federal.
Use apenas o contexto fornecido. Se a pergunta não estiver no contexto, diga:
"Apenas respondo sobre notícias de educação no Distrito Federal."

CONTEXTO:
{contexto}

PERGUNTA:
{pergunta}

RESPOSTA:
"""
prompt = ChatPromptTemplate.from_template(prompt_template)

def answer_question(pergunta: str) -> str:
    docs = retriever.invoke(pergunta)
    contexto = [doc.page_content for doc in docs]
    rag_chain = prompt | llm | StrOutputParser()
    return rag_chain.invoke({"pergunta": pergunta, "contexto": contexto})
