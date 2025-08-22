import requests
import json
import time
import random

def run_crawler():
    """Simula a coleta e tratamento de dados."""
    # A URL aqui é apenas um placeholder. Ela será ajustada quando os contêineres
    # forem executados juntos em uma rede Docker.
    faiss_url = "http://nome_do_container_faiss:8000/add_vector"

    while True:
        # Dados simulados para o FAISS
        vector_data = {
            "vector": [random.random() for _ in range(128)],
            "metadata": {"timestamp": time.time(), "source": "crawler"}
        }

        try:
            # O requests irá falhar aqui porque o host não existe ainda,
            # o que é esperado neste momento.
            response = requests.post(faiss_url, json=vector_data)
            response.raise_for_status()
            print(f"Dados enviados com sucesso: {response.json()}")
        except requests.exceptions.RequestException as e:
            print(f"Erro ao enviar dados (isso é esperado agora): {e}")

        time.sleep(5)

if __name__ == "__main__":
    run_crawler()