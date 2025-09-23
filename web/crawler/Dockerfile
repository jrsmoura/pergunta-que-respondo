FROM python:3.11.13-slim

WORKDIR /app

# Instala as bibliotecas que o seu crawler precisa
RUN pip install requests beautifulsoup4

# Copia o script do crawler para a imagem
COPY crawler_script.py .

# Comando para executar o crawler quando o contêiner for iniciado
CMD ["python", "crawler_script.py"]