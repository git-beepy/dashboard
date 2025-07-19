# Use imagem oficial compatível com Python 3.11
FROM python:3.11-slim

# Define diretório de trabalho
WORKDIR /app

# Copia os arquivos do backend
COPY . .

# Instala dependências
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expõe a porta do Render
EXPOSE 10000

# Comando para rodar o servidor
CMD ["gunicorn", "main:create_app", "--bind", "0.0.0.0:10000", "--workers", "1", "--timeout", "120"]
