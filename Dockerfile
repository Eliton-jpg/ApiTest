FROM python:3.11-alpine

# Cria um grupo e um usuário não-root
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Define o diretório de trabalho
WORKDIR /app

# Copia o arquivo de dependências e instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação para o contêiner
COPY . .

# Ajusta as permissões para o usuário não-root
RUN chown -R appuser:appgroup /app

# Troca para o usuário não-root
USER appuser

# Comando para iniciar a aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
