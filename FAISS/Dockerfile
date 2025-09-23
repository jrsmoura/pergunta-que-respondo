FROM python:3.11.13-slim

WORKDIR /app

# Instala as bibliotecas necessárias para rodar o FAISS e a API
RUN pip install faiss-cpu fastapi uvicorn

# Copia o script da API para a imagem
COPY faiss_server.py .

# Expõe a porta que a API usará
EXPOSE 8000

# Comando para iniciar a API quando o contêiner for executado
CMD ["uvicorn", "faiss_server:app", "--host", "0.0.0.0", "--port", "8000"]