# CRAWLER/crawler_script.py
import os
import time
import random
import requests
from urllib.parse import urljoin

FAISS_BASE = os.getenv("FAISS_URL", "http://faiss:8000")
ADD_VECTOR_URL = urljoin(FAISS_BASE.rstrip("/") + "/", "add_vector")

BACKOFF_OK = 5              # espera entre envios quando OK
BACKOFF_MIN, BACKOFF_MAX = 5, 20  # espera aleatória quando falha

def run_crawler():
    print(f"[crawler] Enviando para: {ADD_VECTOR_URL}")
    while True:
        payload = {
            "vector": [random.random() for _ in range(128)],
            "metadata": {"timestamp": time.time(), "source": "crawler"},
        }
        try:
            r = requests.post(ADD_VECTOR_URL, json=payload, timeout=5)
            r.raise_for_status()
            print(f"[crawler] OK: {r.json()}")
            time.sleep(BACKOFF_OK)
        except requests.RequestException as e:
            print(f"[crawler] Falha ao enviar para {ADD_VECTOR_URL}: {e}")
            time.sleep(random.randint(BACKOFF_MIN, BACKOFF_MAX))

if __name__ == "__main__":
    run_crawler()
