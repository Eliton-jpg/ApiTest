FROM python:3.11-slim

# Atualizar os pacotes do sistema e garantir que o zlib1g esteja atualizado
RUN apt-get update && apt-get upgrade -y && apt-get install -y zlib1g && apt-get clean

WORKDIR /app

# Copie o arquivo de dependências e instale os pacotes Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie o código da aplicação para o contêiner
COPY . .

# Comando para iniciar a aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
