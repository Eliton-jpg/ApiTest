
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends build-essential zlib1g && apt-get clean

WORKDIR /app


COPY requirements.txt .


RUN pip install --no-cache-dir -r requirements.txt

# Copie o código da aplicação para o contêiner
COPY . .

# Comando para iniciar a aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
