"""
**Autor: Victor Kauan**

**Modificação: Robson Ricardo**

Módulo de Coleta de Notícias para o Projeto 'Pergunta que Respondo'.

Este script é responsável por realizar a coleta automatizada de notícias sobre
educação na Região Integrada de Desenvolvimento do Distrito Federal e Entorno (RIDE-DF).
Ele utiliza a API da Tavily para buscar links de notícias relevantes e a API Gemini
do Google para extrair o conteúdo principal de cada página, limpando-o de
elementos desnecessários como menus, anúncios e rodapés.

O processo segue a arquitetura Medallion, salvando os dados brutos extraídos
(camada Bronze) em formato JSON. O script foi projetado para ser executado
diariamente, evitando a duplicidade de coletas através de um log de URLs já
processadas.

Funcionalidades:

- Busca avançada de notícias com base em uma query.
- Extração de conteúdo de páginas web com IA (Gemini).
- Validação para descartar páginas que não são artigos de notícia.
- Persistência dos artigos coletados em arquivos JSON individuais.
- Mecanismo para evitar o reprocessamento de URLs.
- Gerenciamento de chaves de API via variáveis de ambiente (.env).

"""

import os
import json
import hashlib
import logging
from datetime import datetime
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from tavily import TavilyClient

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# ========================
# Configurações iniciais
# ========================
BASE_DIR = Path(__file__).resolve().parent.parent
FAISS_DATA_PATH = BASE_DIR / "FAISS"
BRONZE_DATA_PATH = BASE_DIR / "data" / "bronze"
PROCESSED_URLS_LOG = BRONZE_DATA_PATH / "processed_urls.log"

FAISS_DATA_PATH.mkdir(parents=True, exist_ok=True)
BRONZE_DATA_PATH.mkdir(parents=True, exist_ok=True)

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ========================
# APIs
# ========================
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not TAVILY_API_KEY or not GOOGLE_API_KEY:
    raise ValueError("Faltando TAVILY_API_KEY ou GOOGLE_API_KEY no .env")

tavily = TavilyClient(api_key=TAVILY_API_KEY)

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    google_api_key=GOOGLE_API_KEY,
)

prompt = ChatPromptTemplate.from_template(
    """Você é um especialista em extração de dados de páginas web.
Analise o seguinte texto extraído de um HTML e retorne APENAS o texto limpo e coeso do artigo principal.
Ignore menus, anúncios, rodapés ou textos irrelevantes.
Se não for um artigo válido, retorne exatamente a palavra 'NAO_EH_ARTIGO'.

--- INÍCIO ---
{conteudo}
--- FIM ---
ARTIGO EXTRAÍDO:"""
)

rag_chain = prompt | llm | StrOutputParser()

# ========================
# Funções utilitárias
# ========================
def carregar_urls_processadas() -> set[str]:
    if not PROCESSED_URLS_LOG.exists():
        return set()
    return set(PROCESSED_URLS_LOG.read_text().splitlines())

def salvar_url_processada(url: str, test_mode: bool):
    if test_mode:
        logging.info(f"[TEST_MODE] URL processada (não salva): {url}")
        return
    with open(PROCESSED_URLS_LOG, "a") as f:
        f.write(f"{url}\n")

def extrair_conteudo_com_ia(url: str, session: requests.Session) -> dict | None:
    logging.info(f"Processando: {url}")
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = session.get(url, headers=headers, timeout=20)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "nav", "header", "footer"]):
            tag.decompose()

        html_pre_limpo = soup.get_text(separator="\n", strip=True)

        if len(html_pre_limpo) < 500:
            logging.warning("Descartado: texto muito curto.")
            return None

        texto_extraido = rag_chain.invoke({"conteudo": html_pre_limpo[:15000]})

        if "NAO_EH_ARTIGO" in texto_extraido or len(texto_extraido) < 250:
            logging.info("Veredito: não é artigo válido.")
            return None

        return {"texto": texto_extraido}

    except Exception as e:
        logging.error(f"Erro ao processar {url}: {e}")
        return None

def salvar_artigo_em_json(artigo: dict, test_mode: bool):
    if test_mode:
        logging.info(f"[TEST_MODE] Artigo coletado (não salvo em disco): {artigo['titulo']}")
        return

    url_hash = hashlib.md5(artigo["link"].encode()).hexdigest()[:10]
    timestamp = datetime.now().strftime("%Y-%m-%d")
    filename = f"{timestamp}_{artigo['fonte'].replace('.', '_')}_{url_hash}.json"
    filepath = BRONZE_DATA_PATH / filename

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(artigo, f, ensure_ascii=False, indent=4)
    logging.info(f"Artigo salvo em: {filepath}")

def atualizar_faiss(artigo: dict, test_mode: bool):
    if test_mode:
        logging.info("[TEST_MODE] FAISS não atualizado.")
        return

    texto = f"{artigo['titulo']} - {artigo['texto']}"
    if (FAISS_DATA_PATH / "index.faiss").exists():
        vs = FAISS.load_local(str(FAISS_DATA_PATH), embeddings, allow_dangerous_deserialization=True)
        vs.add_texts([texto])
        logging.info("🔄 Índice FAISS atualizado")
    else:
        vs = FAISS.from_texts([texto], embedding=embeddings)
        logging.info("🆕 Índice FAISS criado")
    vs.save_local(str(FAISS_DATA_PATH))

def executar_coleta(query: str, test_mode: bool = False):
    logging.info(f"Iniciando coleta. Modo teste = {test_mode}")
    try:
        response_tavily = tavily.search(query=query, search_depth="advanced", max_results=5)
        urls_tavily = response_tavily.get("results", [])
    except Exception as e:
        logging.error(f"Erro Tavily: {e}")
        return []

    urls_processadas = carregar_urls_processadas()
    artigos = []

    with requests.Session() as session:
        for item in urls_tavily:
            url = item.get("url")
            if not url or url in urls_processadas:
                continue

            resultado_ia = extrair_conteudo_com_ia(url, session)
            if resultado_ia:
                artigo = {
                    "fonte": item.get("source", url.split("/")[2]),
                    "titulo": item.get("title", "Sem título"),
                    "link": url,
                    "texto": resultado_ia["texto"],
                    "data_coleta": datetime.now().isoformat(),
                    "query_origem": query,
                }
                artigos.append(artigo)
                salvar_artigo_em_json(artigo, test_mode)
                atualizar_faiss(artigo, test_mode)
                salvar_url_processada(url, test_mode)

    logging.info(f"✅ Coleta finalizada: {len(artigos)} artigos.")
    return artigos
