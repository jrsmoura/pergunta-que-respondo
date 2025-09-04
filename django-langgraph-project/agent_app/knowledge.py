import os
import json

data_path = "data/bronze/"
def create_dummies()-> list:
    """Ler arquivos na pasta 'data/bronze/' e cria uma lista com os textos das notícias

    :returns: Lista com textos
    :rtype: list
    """
    texts_list = []
    for f in os.listdir(data_path):
        with open(f) as j:
            d = json.load(j)
            texts_list.append(d["texto"])
    return texts_list
