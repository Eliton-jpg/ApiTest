FROM python:3.11-alpine

# Cria um grupo e um usuário com IDs específicos (1000 é um ID comum)
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Define o diretório de trabalho
WORKDIR /app

# Copia e instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação para o contêiner
COPY . .

# Muda a propriedade dos arquivos para o usuário não-root
RUN chown -R appuser:appgroup /app

# Troca para o usuário não-root
USER appuser

# Comando para iniciar a aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
