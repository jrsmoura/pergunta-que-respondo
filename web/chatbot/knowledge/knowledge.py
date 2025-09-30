"""
Módulo para manipulação de conhecimento no chatbot.
"""

import os
import json

data_path = "data/bronze/"

def create_dummies() -> list:
    """Lê arquivos na pasta 'data/bronze/' e cria uma lista com os textos das notícias"""
    texts_list = []
    for f in os.listdir(data_path):
        file_path = os.path.join(data_path, f)
        if f.endswith(".json"):
            with open(file_path, encoding="utf-8") as j:
                d = json.load(j)
                texts_list.append(d.get("texto", ""))
    return texts_list