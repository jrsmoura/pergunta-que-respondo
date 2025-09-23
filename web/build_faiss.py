from chatbot.knowledge.knowledge import create_dummies
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

def main():
    """
    Gera um índice FAISS a partir de dados de texto fictícios e o salva localmente.

    Esta função executa os seguintes passos:
    1. Exibe uma mensagem indicando o início da geração do índice FAISS.
    2. Cria dados de texto fictícios usando a função `create_dummies()`.
    3. Inicializa um modelo de embeddings HuggingFace com o modelo 'all-MiniLM-L6-v2'.
    4. Constrói um vetor store FAISS a partir dos textos e embeddings.
    5. Salva o índice FAISS gerado no diretório local './FAISS/'.
    6. Exibe uma mensagem de confirmação após o salvamento bem-sucedido.
    """
    print("🔄 Gerando FAISS index...")
    texts = create_dummies()
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_store = FAISS.from_texts(texts, embedding=embeddings)
    vector_store.save_local("FAISS/")
    print("✅ FAISS salvo em ./FAISS/")

if __name__ == "__main__":
    main()