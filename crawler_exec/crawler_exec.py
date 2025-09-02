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
import pandas as pd
from tavily import TavilyClient
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# CONFIGURAÇÃO INICIAL
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# CONFIGURAÇÃO DAS APIS
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not TAVILY_API_KEY or not GEMINI_API_KEY:
    raise ValueError("Chaves de API TAVILY_API_KEY ou GEMINI_API_KEY não encontradas no .env")

tavily = TavilyClient(api_key=TAVILY_API_KEY)
genai.configure(api_key=GEMINI_API_KEY)

# CONFIGURAÇÃO DO MODELO GEMINI
generation_config = {"temperature": 0.2, "top_p": 1, "top_k": 1, "max_output_tokens": 8192}
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]
model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config=generation_config, safety_settings=safety_settings)

# CONSTANTES E DIRETÓRIOS
BRONZE_DATA_PATH = Path("data/bronze")
PROCESSED_URLS_LOG = BRONZE_DATA_PATH / "processed_urls.log"
BRONZE_DATA_PATH.mkdir(parents=True, exist_ok=True)

def carregar_urls_processadas():
    """Carrega o conjunto de URLs já processadas do arquivo de log.

    Esta função lê o arquivo 'processed_urls.log' e retorna um conjunto (set)
    contendo todas as URLs que já foram coletadas e salvas, para evitar
    reprocessamento. Se o arquivo de log não existir, retorna um conjunto vazio.

    :return: Um conjunto de strings, onde cada string é uma URL já processada.
    :rtype: set[str]
    """
    if not PROCESSED_URLS_LOG.exists():
        return set()
    with open(PROCESSED_URLS_LOG, 'r') as f:
        return set(line.strip() for line in f)

def salvar_url_processada(url):
    """Adiciona uma nova URL ao arquivo de log de URLs processadas.

    Após um artigo ser coletado e salvo com sucesso, esta função é chamada
    para registrar a URL no arquivo 'processed_urls.log', garantindo que
    ela não seja coletada novamente em execuções futuras.

    :param url: A URL que foi processada com sucesso.
    :type url: str
    """
    with open(PROCESSED_URLS_LOG, 'a') as f:
        f.write(f"{url}\n")

def extrair_conteudo_com_ia(url: str, session: requests.Session) -> dict | None:
    """Usa a API Gemini para analisar o HTML de uma URL e extrair o conteúdo principal.

    Realiza uma requisição GET para a URL, faz uma pré-limpeza do HTML com
    BeautifulSoup para remover tags irrelevantes (script, style, etc.), e envia
    o texto resultante para a API Gemini. O prompt instrui o modelo a retornar
    apenas o texto do artigo principal ou uma flag 'NAO_EH_ARTIGO' caso o
    conteúdo não seja uma notícia válida.

    :param url: A URL da página da qual o conteúdo será extraído.
    :type url: str
    :param session: A sessão de requests para reutilizar a conexão TCP.
    :type session: requests.Session
    :return: Um dicionário contendo o texto extraído na chave 'texto', ou None
             se a extração falhar ou a página não for um artigo válido.
    :rtype: dict | None
    """
    logging.info(f"Processando com IA: {url}")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    try:
        response = session.get(url, headers=headers, timeout=20)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        for tag in soup(['script', 'style', 'nav', 'header', 'footer']):
            tag.decompose()
        
        html_pre_limpo = soup.get_text(separator='\n', strip=True)

        if len(html_pre_limpo) < 500:
             logging.warning("Descartado: Conteúdo pré-limpeza muito curto.")
             return None

        prompt_parts = [
            "Você é um especialista em extração de dados de páginas web.",
            "Analise o seguinte texto extraído de um HTML e retorne APENAS o texto limpo e coeso do artigo principal.",
            "Ignore qualquer texto de menu, anúncios, links de 'leia também', avisos de cookies ou rodapés.",
            "Se o conteúdo não parecer um artigo de notícia completo (ex: é apenas uma lista de links, uma galeria de fotos ou uma página de erro), retorne EXATAMENTE a palavra 'NAO_EH_ARTIGO'.",
            "\n--- INÍCIO DO TEXTO DA PÁGINA ---\n",
            html_pre_limpo[:15000],
            "\n--- FIM DO TEXTO DA PÁGINA ---\n",
            "ARTIGO EXTRAÍDO:",
        ]
        
        response_ia = model.generate_content(prompt_parts)
        texto_extraido = response_ia.text.strip()

        if "NAO_EH_ARTIGO" in texto_extraido or len(texto_extraido) < 250:
            logging.info("Veredito da IA: Não é um artigo válido.")
            return None

        logging.info("Veredito da IA: Artigo extraído com sucesso.")
        return {"texto": texto_extraido}

    except Exception as e:
        logging.error(f"Erro ao processar a URL {url} com IA: {e}")
        return None

def salvar_artigo_em_json(artigo: dict):
    """Salva um dicionário de artigo como um arquivo JSON na camada Bronze.

    O nome do arquivo é gerado de forma a ser único e informativo, contendo
    a data da coleta, a fonte da notícia e um hash da URL. O arquivo é salvo
    no diretório definido pela constante BRONZE_DATA_PATH.

    :param artigo: Um dicionário contendo os dados do artigo
                   (fonte, titulo, link, texto, etc.).
    :type artigo: dict
    """
    # Gera um hash do link para um nome de arquivo único e curto
    url_hash = hashlib.md5(artigo['link'].encode()).hexdigest()[:10]
    timestamp = datetime.now().strftime("%Y-%m-%d")
    filename = f"{timestamp}_{artigo['fonte'].replace('.', '_')}_{url_hash}.json"
    filepath = BRONZE_DATA_PATH / filename

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(artigo, f, ensure_ascii=False, indent=4)
    logging.info(f"Artigo salvo em: {filepath}")

def executar_coleta(query: str):
    """Orquestra o processo completo de coleta de notícias.

    Esta é a função principal do fluxo de coleta. Ela realiza os seguintes passos:
    1. Busca por uma query na API da Tavily para obter URLs de notícias.
    2. Carrega a lista de URLs já processadas para evitar duplicatas.
    3. Itera sobre as URLs encontradas.
    4. Para cada URL nova, chama `extrair_conteudo_com_ia` para obter o texto.
    5. Se a extração for bem-sucedida, monta o dicionário completo do artigo.
    6. Salva o artigo em um arquivo JSON com `salvar_artigo_em_json`.
    7. Registra a URL como processada com `salvar_url_processada`.

    :param query: A string de busca a ser usada para encontrar notícias relevantes.
    :type query: str
    """
    logging.info(f"Buscando no Tavily pela query: '{query}'")
    
    try:
        response_tavily = tavily.search(query=query, search_depth="advanced", max_results=20)
        urls_tavily = response_tavily.get('results', [])
        logging.info(f"Busca concluída! {len(urls_tavily)} URLs candidatas encontradas.")
    except Exception as e:
        logging.error(f"Falha ao buscar no Tavily: {e}")
        return

    urls_processadas = carregar_urls_processadas()
    artigos_novos_count = 0
    
    with requests.Session() as session:
        for item in urls_tavily:
            url = item.get('url')
            if not url or url in urls_processadas:
                if url in urls_processadas:
                    logging.info(f"URL já processada, pulando: {url}")
                continue

            resultado_ia = extrair_conteudo_com_ia(url, session)

            if resultado_ia:
                artigo_completo = {
                    "fonte": item.get('source', url.split('/')[2]),
                    "titulo": item.get('title', 'Título não encontrado'),
                    "link": url,
                    "texto": resultado_ia['texto'],
                    "data_coleta": datetime.now().isoformat(),
                    "query_origem": query
                }
                salvar_artigo_em_json(artigo_completo)
                salvar_url_processada(url)
                artigos_novos_count += 1
    
    logging.info(f"Processo finalizado. {artigos_novos_count} novos artigos foram coletados e salvos.")

if __name__ == "__main__":
    # EXECUÇÃO PARA COLETA HISTÓRICA
    # Rode este bloco apenas uma vez.
    # [Inference] Ajustando para o ano corrente (2025) para maior relevância nos testes.
    meses_ano = [
        "agosto de 2025", "julho de 2025", "junho de 2025", 
        "maio de 2025", "abril de 2025", "março de 2025"
    ]

    for periodo in meses_ano:
        query_historica = f"notícias sobre educação no Distrito Federal e RIDE em {periodo}"
        executar_coleta(query_historica)

    # EXECUÇÃO PARA COLETA DIÁRIA
    # Comente o bloco acima após o uso e use este para a automação diária.
    # query_diaria = "notícias recentes sobre educação na Região Integrada de Desenvolvimento do Distrito Federal e Entorno (RIDE-DF)"
    # executar_coleta(query_diaria)
